"""
DSA Multi-Language Judge Engine for Boss Battles (Python 3 & C++ 17).
Executes player Python or C++ code against sample or hidden test cases,
enforces timeouts (TLE), captures syntax/compilation/runtime errors (RE),
and computes combat damage:
- 1st-try AC: ONE-SHOT KILL (100% Boss Max HP, -1000 HP)
- 2nd-try AC: HALF HP CUT (50% Boss Max HP, -500 HP)
- Partial / Later AC: Standard 500 HP damage
- WA / TLE / RE: Boss Counter Attack on Player (-200 HP)
"""

import sys
import io
import os
import ast
import time
import shutil
import tempfile
import threading
import subprocess
import traceback
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple


class DSAVerdict(Enum):
    AC = "AC"      # Accepted
    WA = "WA"      # Wrong Answer
    TLE = "TLE"    # Time Limit Exceeded
    RE = "RE"      # Runtime Error / Compilation Error


class DSATestResult:
    def __init__(self, test_idx: int, verdict: DSAVerdict, input_data: Any, expected: Any, actual: Any = None, error_msg: str = "", elapsed_ms: float = 0.0):
        self.test_idx = test_idx
        self.verdict = verdict
        self.input_data = input_data
        self.expected = expected
        self.actual = actual
        self.error_msg = error_msg
        self.elapsed_ms = elapsed_ms


class DSASubmissionReport:
    def __init__(self, problem_id: str, verdict: DSAVerdict, passed_count: int, total_count: int, test_results: List[DSATestResult], summary_msg: str = "", damage_to_boss: int = 0, damage_to_player: int = 0, is_one_shot: bool = False, is_half_hp: bool = False):
        self.problem_id = problem_id
        self.verdict = verdict
        self.passed_count = passed_count
        self.total_count = total_count
        self.test_results = test_results
        self.summary_msg = summary_msg
        self.damage_to_boss = damage_to_boss
        self.damage_to_player = damage_to_player
        self.is_one_shot = is_one_shot
        self.is_half_hp = is_half_hp


def find_cpp_compiler() -> Tuple[Optional[str], Optional[str]]:
    """
    Locates a working C++ compiler on the system:
    1. Native Windows g++ or clang++ in PATH or standard MinGW folders.
    2. WSL Ubuntu g++ via wsl.exe.
    Returns (backend_type, command_or_path): ('native', 'g++') | ('wsl', 'wsl.exe') | (None, None).
    """
    # 1. Native g++ in PATH
    which_gpp = shutil.which("g++")
    if which_gpp:
        return ("native", which_gpp)

    which_clang = shutil.which("clang++")
    if which_clang:
        return ("native", which_clang)

    # 2. Check standard MinGW / CodeBlocks paths
    known_paths = [
        r"C:\MinGW\bin\g++.exe",
        r"C:\msys64\ucrt64\bin\g++.exe",
        r"C:\msys64\mingw64\bin\g++.exe",
        r"C:\TDM-GCC-64\bin\g++.exe",
        r"C:\Program Files\CodeBlocks\MinGW\bin\g++.exe",
        r"D:\MinGW\bin\g++.exe"
    ]
    for p in known_paths:
        if os.path.exists(p):
            return ("native", p)

    # 3. Check WSL g++
    wsl_path = shutil.which("wsl.exe") or shutil.which("wsl")
    if wsl_path:
        try:
            res = subprocess.run([wsl_path, "g++", "--version"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return ("wsl", wsl_path)
        except Exception:
            pass

    return (None, None)


def parse_stdout_value(output_str: str) -> Any:
    """Parses whitespace-separated stdout into numbers, booleans, or lists."""
    s = output_str.strip()
    if not s:
        return ""
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    parts = s.split()
    if len(parts) == 1:
        try:
            return int(parts[0])
        except ValueError:
            try:
                return float(parts[0])
            except ValueError:
                return parts[0]
    # Multiple tokens
    parsed = []
    all_int = True
    for p in parts:
        try:
            parsed.append(int(p))
        except ValueError:
            all_int = False
            parsed.append(p)
    return parsed if all_int else parts


class DSAJudge:
    def __init__(self, time_limit_sec: float = 2.0):
        self.time_limit_sec = time_limit_sec
        self.compiler_backend, self.compiler_path = find_cpp_compiler()

    def evaluate(
        self,
        code_str: str,
        problem: Dict[str, Any],
        attempt_count: int = 1,
        is_sample_run: bool = False,
        language: str = "python"
    ) -> DSASubmissionReport:
        """
        Evaluates player code against tests for the given language ('python' or 'cpp').
        """
        tests = problem.get("sample_tests", []) if is_sample_run else problem.get("hidden_tests", [])
        if not tests:
            tests = problem.get("sample_tests", [])

        lang = language.lower()
        if lang == "cpp":
            return self._evaluate_cpp(code_str, problem, tests, attempt_count, is_sample_run)
        else:
            return self._evaluate_python(code_str, problem, tests, attempt_count, is_sample_run)

    # -------------------------------------------------------------------------
    # PYTHON EVALUATION
    # -------------------------------------------------------------------------
    def _evaluate_python(
        self,
        code_str: str,
        problem: Dict[str, Any],
        tests: List[Dict[str, Any]],
        attempt_count: int,
        is_sample_run: bool
    ) -> DSASubmissionReport:
        # Check syntax first via AST
        try:
            parsed_ast = ast.parse(code_str, filename="<player_solution>")
            compiled_code = compile(parsed_ast, "<player_solution>", "exec")
        except SyntaxError as e:
            err_line = e.lineno if hasattr(e, "lineno") else "?"
            err_text = f"Python SyntaxError on line {err_line}: {e.msg}"
            res = DSATestResult(0, DSAVerdict.RE, None, None, None, error_msg=err_text)
            return self._build_report(problem["id"], DSAVerdict.RE, [res], len(tests), err_text, attempt_count, is_sample_run)

        # Detect if top-level `def solve(...)` exists via AST without running stdin code prematurely
        has_solve_def = any(
            isinstance(node, ast.FunctionDef) and node.name == "solve"
            for node in parsed_ast.body
        )

        sandbox_globals = {"__builtins__": __builtins__}
        has_solve_fn = False
        if has_solve_def:
            try:
                exec(compiled_code, sandbox_globals)
                if callable(sandbox_globals.get("solve")):
                    has_solve_fn = True
            except Exception as e:
                tb = traceback.format_exc().splitlines()
                err_text = f"RuntimeError during initialization: {tb[-1] if tb else str(e)}"
                res = DSATestResult(0, DSAVerdict.RE, None, None, None, error_msg=err_text)
                return self._build_report(problem["id"], DSAVerdict.RE, [res], len(tests), err_text, attempt_count, is_sample_run)

        test_results = []
        overall_verdict = DSAVerdict.AC

        for idx, t in enumerate(tests, 1):
            inp = t.get("input")
            expected = t.get("expected")
            stdin_data = t.get("stdin", "")

            actual = None
            err_msg = ""
            verdict = DSAVerdict.AC
            elapsed_ms = 0.0

            if has_solve_fn:
                # Run solve() in a timed thread
                solve_fn = sandbox_globals["solve"]
                holder = {"output": None, "error": None}

                def target_call():
                    try:
                        if isinstance(inp, dict):
                            holder["output"] = solve_fn(**inp)
                        elif isinstance(inp, (list, tuple)):
                            holder["output"] = solve_fn(*inp)
                        else:
                            holder["output"] = solve_fn(inp)
                    except Exception as ex:
                        holder["error"] = ex

                t0 = time.time()
                th = threading.Thread(target=target_call)
                th.daemon = True
                th.start()
                th.join(self.time_limit_sec)
                elapsed_ms = (time.time() - t0) * 1000

                if th.is_alive():
                    verdict = DSAVerdict.TLE
                    err_msg = f"Time Limit Exceeded (>{self.time_limit_sec}s). Please optimize your solution!"
                elif holder["error"] is not None:
                    verdict = DSAVerdict.RE
                    ex = holder["error"]
                    tb = traceback.format_exception(type(ex), ex, ex.__traceback__)
                    err_msg = tb[-1].strip() if tb else str(ex)
                else:
                    actual = holder["output"]
            else:
                # Mode B: Standard competitive programming script (reads stdin, prints to stdout)
                t0 = time.time()
                if getattr(sys, "frozen", False):
                    # Running inside standalone .exe: sys.executable is the game itself!
                    # Execute safely in-process using redirected StringIO stdin/stdout on a timed thread.
                    holder = {"stdout": "", "error": None}

                    def target_script():
                        old_stdin, old_stdout = sys.stdin, sys.stdout
                        out_buf = io.StringIO()
                        sys.stdin = io.StringIO(stdin_data)
                        sys.stdout = out_buf
                        try:
                            exec(compiled_code, {"__name__": "__main__", "__builtins__": __builtins__})
                            holder["stdout"] = out_buf.getvalue()
                        except SystemExit as sysex:
                            if sysex.code not in (None, 0):
                                holder["error"] = RuntimeError(f"Exited with code {sysex.code}")
                            else:
                                holder["stdout"] = out_buf.getvalue()
                        except Exception as ex:
                            holder["error"] = ex
                        finally:
                            sys.stdin = old_stdin
                            sys.stdout = old_stdout

                    th = threading.Thread(target=target_script)
                    th.daemon = True
                    th.start()
                    th.join(self.time_limit_sec)
                    elapsed_ms = (time.time() - t0) * 1000
                    if th.is_alive():
                        verdict = DSAVerdict.TLE
                        err_msg = f"Time Limit Exceeded (>{self.time_limit_sec}s)!"
                    elif holder["error"] is not None:
                        verdict = DSAVerdict.RE
                        ex = holder["error"]
                        tb = traceback.format_exception(type(ex), ex, ex.__traceback__)
                        err_msg = tb[-1].strip() if tb else str(ex)
                    else:
                        actual = parse_stdout_value(holder["stdout"])
                else:
                    try:
                        proc = subprocess.run(
                            [sys.executable, "-c", code_str],
                            input=stdin_data,
                            capture_output=True,
                            text=True,
                            timeout=self.time_limit_sec
                        )
                        elapsed_ms = (time.time() - t0) * 1000
                        if proc.returncode != 0:
                            verdict = DSAVerdict.RE
                            err_msg = proc.stderr.strip() or f"Exit code {proc.returncode}"
                        else:
                            actual = parse_stdout_value(proc.stdout)
                    except subprocess.TimeoutExpired:
                        elapsed_ms = self.time_limit_sec * 1000
                        verdict = DSAVerdict.TLE
                        err_msg = f"Time Limit Exceeded (>{self.time_limit_sec}s)!"
                    except Exception as ex:
                        verdict = DSAVerdict.RE
                        err_msg = str(ex)

            if verdict == DSAVerdict.AC:
                if self._is_equivalent(problem["id"], actual, expected, inp):
                    test_results.append(DSATestResult(idx, DSAVerdict.AC, inp, expected, actual, elapsed_ms=elapsed_ms))
                else:
                    verdict = DSAVerdict.WA
                    test_results.append(DSATestResult(idx, DSAVerdict.WA, inp, expected, actual, elapsed_ms=elapsed_ms))
                    overall_verdict = DSAVerdict.WA
                    break
            else:
                test_results.append(DSATestResult(idx, verdict, inp, expected, actual, error_msg=err_msg, elapsed_ms=elapsed_ms))
                overall_verdict = verdict
                break

        return self._build_report(problem["id"], overall_verdict, test_results, len(tests), "", attempt_count, is_sample_run)

    # -------------------------------------------------------------------------
    # C++ EVALUATION
    # -------------------------------------------------------------------------
    def _evaluate_cpp(
        self,
        code_str: str,
        problem: Dict[str, Any],
        tests: List[Dict[str, Any]],
        attempt_count: int,
        is_sample_run: bool
    ) -> DSASubmissionReport:
        # Check compiler availability
        backend, compiler = find_cpp_compiler()
        if not backend:
            msg = (
                "Environment Error: g++ or wsl.exe compiler not found!\n"
                "Please install MinGW-w64 (g++) or enable WSL Ubuntu to compile C++."
            )
            res = DSATestResult(0, DSAVerdict.RE, None, None, None, error_msg=msg)
            return self._build_report(problem["id"], DSAVerdict.RE, [res], len(tests), msg, attempt_count, is_sample_run)

        # Create temporary directory for compilation & binaries
        temp_dir = tempfile.mkdtemp(prefix="dsa_cpp_")
        cpp_source = os.path.join(temp_dir, "solution.cpp")
        with open(cpp_source, "w", encoding="utf-8") as f:
            f.write(code_str)

        try:
            if backend == "native":
                bin_path = os.path.join(temp_dir, "solution.exe")
                comp_cmd = [compiler, "-O2", "-std=c++17", "-Wall", cpp_source, "-o", bin_path]
            else:
                # WSL path translation: C:\... -> /mnt/c/...
                drive = cpp_source[0].lower()
                rest = cpp_source[2:].replace("\\", "/")
                wsl_src = f"/mnt/{drive}{rest}"
                wsl_bin = "/tmp/dsa_cpp_solution"
                comp_cmd = [compiler, "g++", "-O2", "-std=c++17", "-Wall", wsl_src, "-o", wsl_bin]

            comp_res = subprocess.run(comp_cmd, capture_output=True, text=True, timeout=12)
            if comp_res.returncode != 0:
                err_text = f"C++ Compilation Error:\n{comp_res.stderr.strip()}"
                res = DSATestResult(0, DSAVerdict.RE, None, None, None, error_msg=err_text)
                return self._build_report(problem["id"], DSAVerdict.RE, [res], len(tests), err_text, attempt_count, is_sample_run)

            # Compilation successful: Execute tests
            test_results = []
            overall_verdict = DSAVerdict.AC

            for idx, t in enumerate(tests, 1):
                inp = t.get("input")
                expected = t.get("expected")
                stdin_data = t.get("stdin", "")

                if backend == "native":
                    exec_cmd = [bin_path]
                else:
                    exec_cmd = [compiler, wsl_bin]

                t0 = time.time()
                try:
                    run_res = subprocess.run(
                        exec_cmd,
                        input=stdin_data,
                        capture_output=True,
                        text=True,
                        timeout=self.time_limit_sec
                    )
                    elapsed_ms = (time.time() - t0) * 1000

                    if run_res.returncode != 0:
                        verdict = DSAVerdict.RE
                        err_msg = run_res.stderr.strip() or f"Runtime error: Exit code {run_res.returncode}"
                        test_results.append(DSATestResult(idx, verdict, inp, expected, None, error_msg=err_msg, elapsed_ms=elapsed_ms))
                        overall_verdict = verdict
                        break

                    actual = parse_stdout_value(run_res.stdout)
                    if self._is_equivalent(problem["id"], actual, expected, inp):
                        test_results.append(DSATestResult(idx, DSAVerdict.AC, inp, expected, actual, elapsed_ms=elapsed_ms))
                    else:
                        test_results.append(DSATestResult(idx, DSAVerdict.WA, inp, expected, actual, elapsed_ms=elapsed_ms))
                        overall_verdict = DSAVerdict.WA
                        break

                except subprocess.TimeoutExpired:
                    elapsed_ms = self.time_limit_sec * 1000
                    test_results.append(DSATestResult(idx, DSAVerdict.TLE, inp, expected, None, error_msg=f"Time Limit Exceeded ({self.time_limit_sec}s)!", elapsed_ms=elapsed_ms))
                    overall_verdict = DSAVerdict.TLE
                    break
                except Exception as ex:
                    test_results.append(DSATestResult(idx, DSAVerdict.RE, inp, expected, None, error_msg=str(ex)))
                    overall_verdict = DSAVerdict.RE
                    break

            return self._build_report(problem["id"], overall_verdict, test_results, len(tests), "", attempt_count, is_sample_run)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # REPORT & DAMAGE CALCULATION
    # -------------------------------------------------------------------------
    def _build_report(
        self,
        problem_id: str,
        overall_verdict: DSAVerdict,
        test_results: List[DSATestResult],
        total_count: int,
        custom_msg: str,
        attempt_count: int,
        is_sample_run: bool
    ) -> DSASubmissionReport:
        passed_count = sum(1 for r in test_results if r.verdict == DSAVerdict.AC)
        damage_to_boss = 0
        damage_to_player = 0
        is_one_shot = False
        is_half_hp = False
        summary_msg = custom_msg

        if is_sample_run:
            if not summary_msg:
                if overall_verdict == DSAVerdict.AC:
                    summary_msg = f"[SAMPLE RUN PASSED] Passed {passed_count}/{total_count} sample tests! Ready to submit."
                else:
                    summary_msg = f"[SAMPLE RUN FAILED: {overall_verdict.value}] Please check test {len(test_results)}."
        else:
            if overall_verdict == DSAVerdict.AC and passed_count == total_count:
                if attempt_count == 1:
                    is_one_shot = True
                    damage_to_boss = 1000
                    summary_msg = summary_msg or ">>> ONE-SHOT KILL! 1st-try AC (-1000 HP)! <<<"
                elif attempt_count == 2:
                    is_half_hp = True
                    damage_to_boss = 500
                    summary_msg = summary_msg or ">>> HALF-HP SLASH! 2nd-try AC (-500 HP)! <<<"
                else:
                    damage_to_boss = 500
                    summary_msg = summary_msg or f">>> ACCEPTED (Attempt {attempt_count})! Dealt 500 damage to Boss! <<<"
            else:
                damage_to_player = 200
                fail_res = test_results[-1] if test_results else None
                fail_idx = fail_res.test_idx if fail_res else 0
                if not summary_msg:
                    if overall_verdict == DSAVerdict.WA:
                        summary_msg = f"WA (Wrong Answer on Test {fail_idx}): Got = {fail_res.actual}, Expected = {fail_res.expected}. Boss counter-attacked (-200 HP)!"
                    elif overall_verdict == DSAVerdict.TLE:
                        summary_msg = f"TLE (Time Limit Exceeded on Test {fail_idx}): Boss counter-attacked (-200 HP)!"
                    else:
                        err = fail_res.error_msg if fail_res else "Runtime Error"
                        summary_msg = f"RE (Error on Test {fail_idx}: {err}). Boss counter-attacked (-200 HP)!"

        return DSASubmissionReport(
            problem_id=problem_id,
            verdict=overall_verdict,
            passed_count=passed_count,
            total_count=total_count,
            test_results=test_results,
            summary_msg=summary_msg,
            damage_to_boss=damage_to_boss,
            damage_to_player=damage_to_player,
            is_one_shot=is_one_shot,
            is_half_hp=is_half_hp
        )

    def _is_equivalent(self, problem_id: str, actual: Any, expected: Any, inp: Any = None) -> bool:
        """Equivalence checker handling flexible comparisons (e.g., Two Sum index permutations, booleans)."""
        if actual == expected:
            return True

        # Boolean equivalence (e.g. YES/True, NO/False)
        if isinstance(expected, bool):
            if isinstance(actual, str):
                if expected and actual.lower() in ("true", "yes", "1"):
                    return True
                if not expected and actual.lower() in ("false", "no", "0"):
                    return True
            return actual == expected

        # Problem 1: Two Sum
        if problem_id == "boss_1_two_pointers":
            if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
                if len(actual) == 2 and len(expected) == 2:
                    if set(actual) == set(expected):
                        return True
                    # Check mathematical condition if input nums is available
                    if inp and isinstance(inp, dict) and "nums" in inp and "target" in inp:
                        nums = inp["nums"]
                        target = inp["target"]
                        i, j = actual[0], actual[1]
                        if isinstance(i, int) and isinstance(j, int):
                            if 0 <= i < len(nums) and 0 <= j < len(nums) and i != j:
                                if nums[i] + nums[j] == target:
                                    return True

        # String representation match
        if str(actual).strip() == str(expected).strip():
            return True

        return False


# Global Judge Instance
dsa_judge = DSAJudge()

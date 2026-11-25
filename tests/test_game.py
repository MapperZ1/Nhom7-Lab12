"""
Automated unit and integration test suite for Robo-Logic: Boss Battle.
Verifies:
- 6 Boss problems schema & metadata (Vietnamese contest statements without CTDL/GT terms)
- Judge Engine: 1st-try One-Shot (-1000 HP), 2nd-try Half-HP (-500 HP), WA, TLE, RE
- Correctness across all 6 stages in Python (both def solve and stdin/stdout)
- Real C++ 17 Compilation & Execution
- File Import System: importing external .py and .cpp files, language auto-detection, reload, sample run & submission
- English UI, White-theme Contest UI & Font size 14 headless rendering + Final Boss Einstein portrait
- Save Manager & Audio Manager integration
"""

import os
import sys
import tempfile
import pygame

# Ensure project root is on sys.path when running `python tests/test_game.py`
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
screen = pygame.display.set_mode((1200, 720))

from src.dsa_problems import DSA_BOSS_PROBLEMS, get_boss_problem
from src.dsa_judge import dsa_judge, DSAVerdict
from src.ui.boss_screen import BossBattleScreen, LIGHT_BG
from src.ui.screens import MainMenuScreen
from src.save_manager import save_manager
from src.audio import audio


def run_tests():
    print("=== STARTING ROBO-LOGIC BOSS BATTLE AUTOMATED TEST SUITE ===")

    # ---------------------------------------------------------
    # TEST 1: 6 Boss Problems Schema & Vietnamese Contest Formatting
    # ---------------------------------------------------------
    assert len(DSA_BOSS_PROBLEMS) == 6, f"Expected 6 Boss problems, got {len(DSA_BOSS_PROBLEMS)}"
    for stg in range(1, 7):
        prob = get_boss_problem(stg)
        assert prob["stage"] == stg, f"Stage mismatch for stage {stg}"
        assert "boss_name" in prob, f"Boss name missing in stage {stg}"
        assert "problem_code" in prob, f"problem_code missing in stage {stg}"
        assert "THỬ THÁCH LẬP TRÌNH" in prob["contest_name"], f"Expected Vietnamese contest framing in stage {stg}"
        # Verify NO CTDL or Giai thuat mentions
        combined_text = (prob["contest_name"] + prob["topic"] + prob["description"]).lower()
        assert "ctdl" not in combined_text and "cấu trúc dữ liệu" not in combined_text and "giải thuật" not in combined_text, f"Unexpected CTDL/GT mention in stage {stg}"
        assert prob["max_hp"] == 1000, f"Max HP must be 1000 in stage {stg}"
        assert len(prob["sample_tests"]) >= 2, f"Stage {stg} needs at least 2 sample tests"
        assert len(prob["hidden_tests"]) >= 4, f"Stage {stg} needs at least 4 hidden tests"
        for t in prob["sample_tests"] + prob["hidden_tests"]:
            assert "stdin" in t, f"stdin format missing in test of stage {stg}"
            assert "expected_stdout" in t, f"expected_stdout missing in test of stage {stg}"
    print("[PASS] Test 1: 6 Boss problems schema & Vietnamese contest formatting (no CTDL/GT) verified.")

    # ---------------------------------------------------------
    # TEST 2: DSA Judge - 1st-try AC One-Shot Kill (-1000 HP)
    # ---------------------------------------------------------
    p1 = get_boss_problem(1)
    code_p1 = (
        "def solve(nums, target):\n"
        "    seen = {}\n"
        "    for i, x in enumerate(nums):\n"
        "        diff = target - x\n"
        "        if diff in seen:\n"
        "            return [seen[diff], i]\n"
        "        seen[x] = i\n"
        "    return [-1, -1]\n"
    )
    rep_1st = dsa_judge.evaluate(code_p1, p1, attempt_count=1, is_sample_run=False, language="python")
    assert rep_1st.verdict == DSAVerdict.AC, f"Expected AC, got {rep_1st.verdict}"
    assert rep_1st.is_one_shot == True, "1st-try AC must trigger is_one_shot = True!"
    assert rep_1st.damage_to_boss == 1000
    print("[PASS] Test 2: DSA Judge 1st-try AC One-Shot Kill (-1000 HP) verified.")

    # ---------------------------------------------------------
    # TEST 3: DSA Judge - 2nd-try AC Half-HP Cut (-500 HP)
    # ---------------------------------------------------------
    rep_2nd = dsa_judge.evaluate(code_p1, p1, attempt_count=2, is_sample_run=False, language="python")
    assert rep_2nd.verdict == DSAVerdict.AC
    assert rep_2nd.is_half_hp == True
    assert rep_2nd.damage_to_boss == 500
    print("[PASS] Test 3: DSA Judge 2nd-try AC Half-HP Cut (-500 HP) verified.")

    # ---------------------------------------------------------
    # TEST 4: DSA Judge - 3rd-try AC Standard Damage (500 HP)
    # ---------------------------------------------------------
    rep_3rd = dsa_judge.evaluate(code_p1, p1, attempt_count=3, is_sample_run=False, language="python")
    assert rep_3rd.verdict == DSAVerdict.AC
    assert rep_3rd.is_one_shot == False
    assert rep_3rd.is_half_hp == False
    assert rep_3rd.damage_to_boss == 500
    print("[PASS] Test 4: DSA Judge 3rd-try AC standard damage (500 HP) verified.")

    # ---------------------------------------------------------
    # TEST 5: DSA Judge - Wrong Answer (WA) & Boss Counter Attack
    # ---------------------------------------------------------
    code_wa = "def solve(nums, target):\n    return [-999, -999]\n"
    rep_wa = dsa_judge.evaluate(code_wa, p1, attempt_count=1, is_sample_run=False, language="python")
    assert rep_wa.verdict == DSAVerdict.WA
    assert rep_wa.damage_to_player == 200
    assert rep_wa.damage_to_boss == 0
    print("[PASS] Test 5: DSA Judge Wrong Answer (WA) & Boss Counter Attack (-200 HP) verified.")

    # ---------------------------------------------------------
    # TEST 6: DSA Judge - Time Limit Exceeded (TLE) Timeout Protection
    # ---------------------------------------------------------
    code_tle = "def solve(nums, target):\n    while True:\n        pass\n"
    rep_tle = dsa_judge.evaluate(code_tle, p1, attempt_count=1, is_sample_run=False, language="python")
    assert rep_tle.verdict == DSAVerdict.TLE
    assert rep_tle.damage_to_player == 200
    print("[PASS] Test 6: DSA Judge Time Limit Exceeded (TLE) & timeout protection verified.")

    # ---------------------------------------------------------
    # TEST 7: DSA Judge - Syntax & Runtime Error (RE)
    # ---------------------------------------------------------
    code_re = "def solve(nums, target)\n    invalid syntax here!"
    rep_re = dsa_judge.evaluate(code_re, p1, attempt_count=1, is_sample_run=False, language="python")
    assert rep_re.verdict == DSAVerdict.RE
    assert rep_re.damage_to_player > 0
    print("[PASS] Test 7: DSA Judge Syntax / Runtime Error (RE) capture verified.")

    # ---------------------------------------------------------
    # TEST 8: Python Standard I/O Script (stdin/stdout without def solve)
    # ---------------------------------------------------------
    code_p1_stdin = (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n, target = int(data[0]), int(data[1])\n"
        "nums = list(map(int, data[2:2+n]))\n"
        "seen = {}\n"
        "ans = (-1, -1)\n"
        "for i, x in enumerate(nums):\n"
        "    if target - x in seen:\n"
        "        ans = (seen[target - x], i)\n"
        "        break\n"
        "    seen[x] = i\n"
        "print(ans[0], ans[1])\n"
    )
    rep_stdin = dsa_judge.evaluate(code_p1_stdin, p1, attempt_count=1, is_sample_run=False, language="python")
    assert rep_stdin.verdict == DSAVerdict.AC, f"Expected AC for Python stdin/stdout, got {rep_stdin.verdict}"
    print("[PASS] Test 8: Python Standard I/O script (stdin/stdout) verified.")

    # ---------------------------------------------------------
    # TEST 9-14: Algorithmic Solves for Stages 1..6
    # ---------------------------------------------------------
    p1_res = dsa_judge.evaluate(code_p1, p1, attempt_count=1, language="python")
    assert p1_res.verdict == DSAVerdict.AC and p1_res.passed_count == p1_res.total_count
    print("[PASS] Test 9: Stage 1 Algorithmic Solve (Two Pointers / HashMap) verified.")

    p2 = get_boss_problem(2)
    code_p2 = (
        "def solve(s):\n"
        "    stack = []\n"
        "    mapping = {')': '(', '}': '{', ']': '['}\n"
        "    for ch in s:\n"
        "        if ch in mapping:\n"
        "            if not stack or stack[-1] != mapping[ch]:\n"
        "                return False\n"
        "            stack.pop()\n"
        "        else:\n"
        "            stack.append(ch)\n"
        "    return len(stack) == 0\n"
    )
    p2_res = dsa_judge.evaluate(code_p2, p2, attempt_count=1, language="python")
    assert p2_res.verdict == DSAVerdict.AC and p2_res.passed_count == p2_res.total_count
    print("[PASS] Test 10: Stage 2 Algorithmic Solve (Stack LIFO) verified.")

    p3 = get_boss_problem(3)
    code_p3 = (
        "import heapq\n"
        "def solve(nums, k):\n"
        "    min_heap = []\n"
        "    for x in nums:\n"
        "        heapq.heappush(min_heap, x)\n"
        "        if len(min_heap) > k:\n"
        "            heapq.heappop(min_heap)\n"
        "    return min_heap[0]\n"
    )
    p3_res = dsa_judge.evaluate(code_p3, p3, attempt_count=1, language="python")
    assert p3_res.verdict == DSAVerdict.AC and p3_res.passed_count == p3_res.total_count
    print("[PASS] Test 11: Stage 3 Algorithmic Solve (Priority Queue / Heap) verified.")

    p4 = get_boss_problem(4)
    code_p4 = (
        "def solve(trees, m):\n"
        "    low, high, ans = 0, max(trees), 0\n"
        "    while low <= high:\n"
        "        mid = (low + high) // 2\n"
        "        wood = sum(h - mid for h in trees if h > mid)\n"
        "        if wood >= m:\n"
        "            ans = mid\n"
        "            low = mid + 1\n"
        "        else:\n"
        "            high = mid - 1\n"
        "    return ans\n"
    )
    p4_res = dsa_judge.evaluate(code_p4, p4, attempt_count=1, language="python")
    assert p4_res.verdict == DSAVerdict.AC and p4_res.passed_count == p4_res.total_count
    print("[PASS] Test 12: Stage 4 Algorithmic Solve (Binary Search on Answer) verified.")

    p5 = get_boss_problem(5)
    code_p5 = (
        "from collections import deque\n"
        "def solve(grid):\n"
        "    R, C = len(grid), len(grid[0])\n"
        "    if grid[0][0] == 1 or grid[R-1][C-1] == 1:\n"
        "        return -1\n"
        "    queue = deque([(0, 0, 0)])\n"
        "    visited = {(0, 0)}\n"
        "    while queue:\n"
        "        r, c, dist = queue.popleft()\n"
        "        if r == R - 1 and c == C - 1:\n"
        "            return dist\n"
        "        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:\n"
        "            nr, nc = r + dr, c + dc\n"
        "            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 0:\n"
        "                if (nr, nc) not in visited:\n"
        "                    visited.add((nr, nc))\n"
        "                    queue.append((nr, nc, dist + 1))\n"
        "    return -1\n"
    )
    p5_res = dsa_judge.evaluate(code_p5, p5, attempt_count=1, language="python")
    assert p5_res.verdict == DSAVerdict.AC and p5_res.passed_count == p5_res.total_count
    print("[PASS] Test 13: Stage 5 Algorithmic Solve (Graph BFS) verified.")

    p6 = get_boss_problem(6)
    code_p6 = (
        "def solve(weights, values, capacity):\n"
        "    dp = [0] * (capacity + 1)\n"
        "    for w, v in zip(weights, values):\n"
        "        for cap in range(capacity, w - 1, -1):\n"
        "            dp[cap] = max(dp[cap], dp[cap - w] + v)\n"
        "    return dp[capacity]\n"
    )
    p6_res = dsa_judge.evaluate(code_p6, p6, attempt_count=1, language="python")
    assert p6_res.verdict == DSAVerdict.AC and p6_res.passed_count == p6_res.total_count
    print("[PASS] Test 14: Stage 6 Algorithmic Solve (0/1 Knapsack DP) verified.")

    # ---------------------------------------------------------
    # TEST 15: C++ 17 Compilation & Solve for Two Sum
    # ---------------------------------------------------------
    cpp_p1 = (
        "#include <iostream>\n"
        "#include <vector>\n"
        "#include <unordered_map>\n"
        "using namespace std;\n"
        "int main() {\n"
        "    int n, target;\n"
        "    if (!(cin >> n >> target)) return 0;\n"
        "    vector<int> a(n);\n"
        "    unordered_map<int, int> seen;\n"
        "    int ans1 = -1, ans2 = -1;\n"
        "    for (int i = 0; i < n; i++) {\n"
        "        cin >> a[i];\n"
        "        int diff = target - a[i];\n"
        "        if (ans1 == -1 && seen.count(diff)) {\n"
        "            ans1 = seen[diff];\n"
        "            ans2 = i;\n"
        "        }\n"
        "        seen[a[i]] = i;\n"
        "    }\n"
        "    cout << ans1 << \" \" << ans2 << endl;\n"
        "    return 0;\n"
        "}\n"
    )
    cpp_res = dsa_judge.evaluate(cpp_p1, p1, attempt_count=1, is_sample_run=False, language="cpp")
    assert cpp_res.verdict == DSAVerdict.AC, f"Expected C++ AC, got {cpp_res.verdict}: {cpp_res.summary_msg}"
    assert cpp_res.damage_to_boss == 1000
    print("[PASS] Test 15: Real C++ 17 Compilation & Execution (Two Sum AC) verified.")

    # ---------------------------------------------------------
    # TEST 16: File Import System (.py & .cpp) + Reload + Combat
    # ---------------------------------------------------------
    battle = BossBattleScreen(on_back_to_menu=lambda: None)
    assert battle.current_stage == 1
    assert battle.active_tab == "PROBLEM"

    # Verify White Theme & Font Size 14
    assert LIGHT_BG == (255, 255, 255), "Contest background must be pure white!"
    assert battle.terminal.theme == "light"
    assert battle.terminal.font_term.get_height() >= 14

    # Create temporary .py file and import into Stage 1
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(code_p1)
        py_path = tf.name

    # Create temporary .cpp file and import into Stage 2/1 test
    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False, encoding="utf-8") as tf_cpp:
        tf_cpp.write(cpp_p1)
        cpp_path = tf_cpp.name

    try:
        ok = battle.import_solution_file(py_path)
        assert ok, "Python file import failed!"
        imp1 = battle._get_current_imported()
        assert imp1 is not None and imp1["language"] == "python"

        # Run sample tests safely
        battle.run_sample_test()
        assert battle.last_report.verdict == DSAVerdict.AC
        assert battle.boss_target_hp == 1000, "Sample test run must NOT deal boss damage!"

        # Submit imported Python file -> One-Shot Kill!
        battle.submit_solution()
        assert battle.boss_target_hp == 0, f"Expected Boss HP 0 on 1st-try One-Shot, got {battle.boss_target_hp}"

        # Reset battle and test importing C++ file + reload
        battle.reset_current_battle()
        assert battle.boss_target_hp == 1000
        ok_cpp = battle.import_solution_file(cpp_path)
        assert ok_cpp, "C++ file import failed!"
        assert battle._get_current_imported()["language"] == "cpp"
        battle.reload_imported_file()
        assert battle._get_current_imported()["language"] == "cpp"
        print("[PASS] Test 16: File Import (.py & .cpp), Reload, Sample Test & Boss One-Shot verified.")

        # ---------------------------------------------------------
        # TEST 17: Drag & Drop File Event + White UI Rendering
        # ---------------------------------------------------------
        drop_ev = pygame.event.Event(pygame.DROPFILE, file=py_path)
        battle.handle_event(drop_ev)
        assert battle.active_tab == "IMPORT", "Dropping file should auto-switch to IMPORT tab!"
        assert battle._get_current_imported()["language"] == "python"

        # Render both tabs headlessly to ensure zero font/surface errors
        battle.flash_alpha = 0
        battle.switch_main_tab("PROBLEM")
        battle.render(screen)
        battle.switch_main_tab("IMPORT")
        battle.render(screen)
        px_col = screen.get_at((5, 50))[:3]
        assert px_col == (255, 255, 255), f"Contest screen background pixel must be white, got {px_col}"

        # Verify Stage 6 Final Boss (Einstein) portrait & Main Robot sprite load & render cleanly
        menu = MainMenuScreen(lambda: None, lambda: None, lambda: True, lambda: None)
        assert menu.hero_sprite is not None, "MainMenuScreen pixel robot sprite failed to load!"
        menu.draw(screen, 100)

        assert battle.player_sprite is not None, "BossBattleScreen pixel robot sprite failed to load!"
        battle.switch_stage(6)
        assert battle.boss_data["boss_shape"] == "einstein"
        assert "einstein" in battle.boss_portraits, "Final boss Einstein portrait failed to load!"
        battle.switch_main_tab("PROBLEM")
        battle.render(screen)
        print("[PASS] Test 17: Drag & Drop, White-Theme Font-14 UI, Main Robot & Final Boss Einstein verified.")
    finally:
        if os.path.exists(py_path):
            os.remove(py_path)
        if os.path.exists(cpp_path):
            os.remove(cpp_path)

    # ---------------------------------------------------------
    # TEST 18: Save Manager & Audio Integration
    # ---------------------------------------------------------
    save_manager.record_boss_defeat(1, is_one_shot=True, attempts=1)
    assert save_manager.is_boss_slain(1) == True
    assert save_manager.is_boss_one_shot(1) == True

    initial_mute = audio.enabled
    audio.toggle_mute()
    assert audio.enabled != initial_mute
    audio.toggle_mute()
    assert audio.enabled == initial_mute
    print("[PASS] Test 18: Save Manager boss defeat persistence & Audio Manager verified.")

    print("\n>>> ALL 18 TEST SUITES PASSED FLAWLESSLY! <<<")


if __name__ == "__main__":
    run_tests()

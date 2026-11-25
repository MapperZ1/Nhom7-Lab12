"""
Contest Problems for Robo-Logic: Boss Battle.
6 coding challenges written in Vietnamese for the contest sheet.
"""

from typing import Dict, Any, List

DSA_BOSS_PROBLEMS: List[Dict[str, Any]] = [
    {
        "id": "boss_1_two_pointers",
        "stage": 1,
        "problem_code": "TWOSUM",
        "boss_name": "SLIME TỔNG SỐ",
        "boss_title": "Hộ Vệ Thử Thách Cặp Số",
        "topic": "Mảng số nguyên & Tìm cặp phần tử",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 1",
        "file_py": "twosum.py",
        "file_cpp": "twosum.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(nums, target)",
        "max_hp": 1000,
        "theme_color": (29, 78, 216),
        "boss_shape": "slime",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Cho một mảng số nguyên A gồm N phần tử và một số nguyên Target.\n"
            "Hãy tìm đúng hai vị trí chỉ số i và j (0-indexed, với i != j) sao cho tổng hai phần tử bằng Target:\n"
            "    A[i] + A[j] == Target\n"
            "Nếu có nhiều cặp thỏa mãn, có thể trả về bất kỳ cặp hợp lệ nào.\n"
            "Nếu không tồn tại, trả về [-1, -1] (hoặc in ra -1 -1).\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Dòng 1 chứa 2 số nguyên N và Target. Dòng 2 chứa N số nguyên A[0..N-1].\n"
            "  + Output (stdout): In ra 2 chỉ số i và j cách nhau bởi dấu cách (hoặc '-1 -1').\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(nums, target) trả về danh sách [i, j].\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 2 <= N <= 10^5; -10^9 <= A[k] <= 10^9."
        ),
        "input_format": "solve(nums: list[int], target: int) -> list[int] | stdin: Dòng 1: N Target; Dòng 2: N số",
        "output_format": "Trả về [i, j] hoặc in ra 'i j' trên stdout",
        "constraints": "2 <= N <= 10^5, -10^9 <= A[k] <= 10^9",
        "sample_tests": [
            {
                "input": {"nums": [2, 7, 11, 15], "target": 9},
                "stdin": "4 9\n2 7 11 15\n",
                "expected": [0, 1],
                "expected_stdout": "0 1",
                "explanation": "A[0] + A[1] = 2 + 7 = 9 (khớp Target = 9)."
            },
            {
                "input": {"nums": [3, 2, 4], "target": 6},
                "stdin": "3 6\n3 2 4\n",
                "expected": [1, 2],
                "expected_stdout": "1 2",
                "explanation": "A[1] + A[2] = 2 + 4 = 6 (khớp Target = 6)."
            },
            {
                "input": {"nums": [3, 3], "target": 6},
                "stdin": "2 6\n3 3\n",
                "expected": [0, 1],
                "expected_stdout": "0 1",
                "explanation": "A[0] + A[1] = 3 + 3 = 6 (hai chỉ số phân biệt 0 và 1)."
            }
        ],
        "hidden_tests": [
            {"input": {"nums": [1, 5, 8, 12, 19], "target": 20}, "stdin": "5 20\n1 5 8 12 19\n", "expected": [0, 4], "expected_stdout": "0 4"},
            {"input": {"nums": [-3, 4, 3, 90], "target": 0}, "stdin": "4 0\n-3 4 3 90\n", "expected": [0, 2], "expected_stdout": "0 2"},
            {"input": {"nums": [1, 2, 3, 4, 5], "target": 10}, "stdin": "5 10\n1 2 3 4 5\n", "expected": [-1, -1], "expected_stdout": "-1 -1"},
            {"input": {"nums": [10, 20, 30, 40, 50, 60], "target": 90}, "stdin": "6 90\n10 20 30 40 50 60\n", "expected": [2, 5], "expected_stdout": "2 5"},
            {"input": {"nums": [0, 4, 3, 0], "target": 0}, "stdin": "4 0\n0 4 3 0\n", "expected": [0, 3], "expected_stdout": "0 3"},
            {"input": {"nums": [1000000, -500000, 200000, 700000], "target": 200000}, "stdin": "4 200000\n1000000 -500000 200000 700000\n", "expected": [1, 3], "expected_stdout": "1 3"}
        ]
    },
    {
        "id": "boss_2_stack",
        "stage": 2,
        "problem_code": "BRACKETS",
        "boss_name": "GOLEM DẤU NGOẶC",
        "boss_title": "Thạch Thủ Lĩnh Biểu Thức",
        "topic": "Xử lý chuỗi ký tự ngoặc",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 2",
        "file_py": "brackets.py",
        "file_cpp": "brackets.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(s)",
        "max_hp": 1000,
        "theme_color": (194, 65, 12),
        "boss_shape": "golem",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Cho một chuỗi ký tự S chỉ bao gồm các ký tự ngoặc: '(', ')', '{', '}', '[', ']'.\n"
            "Hãy kiểm tra xem chuỗi ngoặc S có hợp lệ hay không theo 3 điều kiện:\n"
            "1. Mọi dấu mở ngoặc phải được đóng bởi đúng dấu ngoặc cùng loại tương ứng.\n"
            "2. Các cặp ngoặc lồng nhau phải đóng theo đúng thứ tự (mở sau đóng trước).\n"
            "3. Mọi dấu đóng ngoặc đều phải có dấu mở ngoặc tương ứng trước đó.\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Một dòng duy nhất chứa chuỗi S.\n"
            "  + Output (stdout): In ra 'YES' (hoặc 'True') nếu hợp lệ; ngược lại in ra 'NO' (hoặc 'False').\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(s) trả về giá trị bool (True / False).\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 1 <= len(S) <= 10^5."
        ),
        "input_format": "solve(s: str) -> bool | stdin: Dòng 1 chứa chuỗi S",
        "output_format": "Trả về True/False hoặc in ra YES/NO trên stdout",
        "constraints": "1 <= len(S) <= 10^5",
        "sample_tests": [
            {
                "input": {"s": "()"},
                "stdin": "()\n",
                "expected": True,
                "expected_stdout": "YES",
                "explanation": "Cặp ngoặc đơn mở và đóng hợp lệ."
            },
            {
                "input": {"s": "()[]{}"},
                "stdin": "()[]{}\n",
                "expected": True,
                "expected_stdout": "YES",
                "explanation": "Các loại ngoặc đóng mở liên tiếp đúng loại."
            },
            {
                "input": {"s": "(]"},
                "stdin": "(]\n",
                "expected": False,
                "expected_stdout": "NO",
                "explanation": "Mở ngoặc tròn '(' nhưng đóng bằng ngoặc vuông ']' -> không hợp lệ."
            }
        ],
        "hidden_tests": [
            {"input": {"s": "([{}])"}, "stdin": "([{}])\n", "expected": True, "expected_stdout": "YES"},
            {"input": {"s": "[(])"}, "stdin": "[(])\n", "expected": False, "expected_stdout": "NO"},
            {"input": {"s": "{[()()]}"}, "stdin": "{[()()]}\n", "expected": True, "expected_stdout": "YES"},
            {"input": {"s": "(((((((("}, "stdin": "((((((((\n", "expected": False, "expected_stdout": "NO"},
            {"input": {"s": "))))))))"}, "stdin": "))))))))\n", "expected": False, "expected_stdout": "NO"},
            {"input": {"s": "{[]}"}, "stdin": "{[]}\n", "expected": True, "expected_stdout": "YES"},
            {"input": {"s": "[({}){[]}]"}, "stdin": "[({}){[]}]\n", "expected": True, "expected_stdout": "YES"},
            {"input": {"s": "}{"}, "stdin": "}{\n", "expected": False, "expected_stdout": "NO"}
        ]
    },
    {
        "id": "boss_3_heap",
        "stage": 3,
        "problem_code": "HEAPK",
        "boss_name": "THỦY QUÁI THỨ TỰ",
        "boss_title": "Xà Vương Giá Trị Lớn Thứ K",
        "topic": "Tìm kiếm phần tử thứ hạng K",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 3",
        "file_py": "heapk.py",
        "file_cpp": "heapk.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(nums, k)",
        "max_hp": 1000,
        "theme_color": (14, 116, 144),
        "boss_shape": "serpent",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Cho dãy số nguyên A gồm N phần tử và một số nguyên dương K (1 <= K <= N).\n"
            "Hãy tìm giá trị của phần tử LỚN THỨ K trong dãy số.\n"
            "Lưu ý: Đây là phần tử lớn thứ K theo thứ tự sắp xếp giảm dần (tính cả các giá trị trùng lặp),\n"
            "không phải phần tử phân biệt thứ K.\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Dòng 1 chứa N và K. Dòng 2 chứa N số nguyên A[0..N-1].\n"
            "  + Output (stdout): In ra một số nguyên duy nhất là phần tử lớn thứ K.\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(nums, k) trả về số nguyên kết quả.\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 1 <= K <= N <= 10^5; -10^4 <= A[i] <= 10^4."
        ),
        "input_format": "solve(nums: list[int], k: int) -> int | stdin: Dòng 1: N K; Dòng 2: N số",
        "output_format": "Trả về số nguyên hoặc in ra stdout",
        "constraints": "1 <= K <= N <= 10^5, -10^4 <= A[i] <= 10^4",
        "sample_tests": [
            {
                "input": {"nums": [3, 2, 1, 5, 6, 4], "k": 2},
                "stdin": "6 2\n3 2 1 5 6 4\n",
                "expected": 5,
                "expected_stdout": "5",
                "explanation": "Sắp xếp giảm dần: [6, 5, 4, 3, 2, 1]. Phần tử lớn thứ 2 là 5."
            },
            {
                "input": {"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4},
                "stdin": "9 4\n3 2 3 1 2 4 5 5 6\n",
                "expected": 4,
                "expected_stdout": "4",
                "explanation": "Sắp xếp giảm dần: [6, 5, 5, 4, 3, 3, 2, 2, 1]. Phần tử lớn thứ 4 là 4."
            }
        ],
        "hidden_tests": [
            {"input": {"nums": [1], "k": 1}, "stdin": "1 1\n1\n", "expected": 1, "expected_stdout": "1"},
            {"input": {"nums": [7, 10, 4, 3, 20, 15], "k": 3}, "stdin": "6 3\n7 10 4 3 20 15\n", "expected": 10, "expected_stdout": "10"},
            {"input": {"nums": [-1, -2, -3, -4], "k": 1}, "stdin": "4 1\n-1 -2 -3 -4\n", "expected": -1, "expected_stdout": "-1"},
            {"input": {"nums": [100, 200, 300, 400, 500], "k": 5}, "stdin": "5 5\n100 200 300 400 500\n", "expected": 100, "expected_stdout": "100"},
            {"input": {"nums": [9, 9, 9, 9, 9], "k": 3}, "stdin": "5 3\n9 9 9 9 9\n", "expected": 9, "expected_stdout": "9"},
            {"input": {"nums": [12, 3, 5, 7, 19, 1, 4, 26], "k": 2}, "stdin": "8 2\n12 3 5 7 19 1 4 26\n", "expected": 19, "expected_stdout": "19"}
        ]
    },
    {
        "id": "boss_4_binary_search",
        "stage": 4,
        "problem_code": "WOODCUT",
        "boss_name": "HỎA LONG LÂM TRƯỜNG",
        "boss_title": "Bá Chủ Cắt Gỗ Tối Ưu",
        "topic": "Tìm kiếm giá trị cắt gỗ tối ưu",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 4",
        "file_py": "woodcut.py",
        "file_cpp": "woodcut.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(trees, m)",
        "max_hp": 1000,
        "theme_color": (185, 28, 28),
        "boss_shape": "dragon",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Có N cây gỗ với chiều cao lần lượt là H_1, H_2, ..., H_N mét. Bạn cần thu thập ít nhất M mét gỗ.\n"
            "Máy cưa có thể thiết lập độ cao lưỡi cưa ở mức nguyên H. Khi cưa, mọi cây cao hơn H đều bị cắt\n"
            "phần ngọn phía trên H (lượng gỗ thu được từ cây i là max(0, H_i - H)).\n"
            "Hãy tìm độ cao lưỡi cưa H LỚN NHẤT sao cho tổng lượng gỗ cắt được >= M.\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Dòng 1 chứa N và M. Dòng 2 chứa N số nguyên H_1..H_N.\n"
            "  + Output (stdout): In ra một số nguyên duy nhất là độ cao H lớn nhất tìm được.\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(trees, m) trả về số nguyên H.\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 1 <= N <= 10^5; 1 <= M, H_i <= 10^9."
        ),
        "input_format": "solve(trees: list[int], m: int) -> int | stdin: Dòng 1: N M; Dòng 2: N số",
        "output_format": "Trả về số nguyên H hoặc in ra stdout",
        "constraints": "1 <= N <= 10^5, 1 <= M, H_i <= 10^9",
        "sample_tests": [
            {
                "input": {"trees": [20, 15, 10, 17], "m": 7},
                "stdin": "4 7\n20 15 10 17\n",
                "expected": 15,
                "expected_stdout": "15",
                "explanation": "Đặt H = 15: Cây 20 cắt được 5m, cây 17 cắt được 2m. Tổng = 7m >= 7."
            },
            {
                "input": {"trees": [4, 42, 40, 26, 46], "m": 20},
                "stdin": "5 20\n4 42 40 26 46\n",
                "expected": 36,
                "expected_stdout": "36",
                "explanation": "Đặt H = 36: (42-36) + (40-36) + (46-36) = 6 + 4 + 10 = 20m."
            }
        ],
        "hidden_tests": [
            {"input": {"trees": [10, 10, 10, 10], "m": 4}, "stdin": "4 4\n10 10 10 10\n", "expected": 9, "expected_stdout": "9"},
            {"input": {"trees": [100], "m": 30}, "stdin": "1 30\n100\n", "expected": 70, "expected_stdout": "70"},
            {"input": {"trees": [1, 2, 3, 4, 5], "m": 15}, "stdin": "5 15\n1 2 3 4 5\n", "expected": 0, "expected_stdout": "0"},
            {"input": {"trees": [50, 60, 70, 80, 90], "m": 100}, "stdin": "5 100\n50 60 70 80 90\n", "expected": 50, "expected_stdout": "50"},
            {"input": {"trees": [1000, 2000, 3000, 4000], "m": 2500}, "stdin": "4 2500\n1000 2000 3000 4000\n", "expected": 2250, "expected_stdout": "2250"},
            {"input": {"trees": [25, 30, 40, 55], "m": 30}, "stdin": "4 30\n25 30 40 55\n", "expected": 32, "expected_stdout": "32"}
        ]
    },
    {
        "id": "boss_5_graph_bfs",
        "stage": 5,
        "problem_code": "MAZE",
        "boss_name": "BÓNG MA MÊ CUNG",
        "boss_title": "Lãnh Chúa Ma Trận Lưới",
        "topic": "Tìm đường đi ngắn nhất trên lưới",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 5",
        "file_py": "maze.py",
        "file_cpp": "maze.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(grid)",
        "max_hp": 1000,
        "theme_color": (109, 40, 217),
        "boss_shape": "phantom",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Cho ma trận mê cung kích thước R x C gồm giá trị 0 (ô trống đi được) và 1 (tường chặn).\n"
            "Xuất phát từ ô (0, 0) và cần di chuyển tới ô đích (R-1, C-1).\n"
            "Mỗi bước đi có thể sang 4 ô kề cạnh (trên, dưới, trái, phải). Hãy tìm số bước đi ít nhất.\n"
            "Nếu ô đầu/cuối bị chặn hoặc không có đường đi hợp lệ, trả về -1.\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Dòng 1 chứa R và C. R dòng tiếp theo mỗi dòng C số nguyên (0 hoặc 1).\n"
            "  + Output (stdout): In ra một số nguyên là số bước ngắn nhất, hoặc -1 nếu không đi được.\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(grid) trả về số nguyên.\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 1 <= R, C <= 100."
        ),
        "input_format": "solve(grid: list[list[int]]) -> int | stdin: Dòng 1: R C; R dòng tiếp theo: C số",
        "output_format": "Trả về số nguyên số bước hoặc in ra stdout",
        "constraints": "1 <= R, C <= 100, grid[r][c] in {0, 1}",
        "sample_tests": [
            {
                "input": {
                    "grid": [
                        [0, 0, 0],
                        [1, 1, 0],
                        [1, 1, 0]
                    ]
                },
                "stdin": "3 3\n0 0 0\n1 1 0\n1 1 0\n",
                "expected": 4,
                "expected_stdout": "4",
                "explanation": "Đường đi ngắn nhất: (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2) gồm 4 bước."
            },
            {
                "input": {
                    "grid": [
                        [0, 1],
                        [1, 0]
                    ]
                },
                "stdin": "2 2\n0 1\n1 0\n",
                "expected": -1,
                "expected_stdout": "-1",
                "explanation": "Các ô kề (0,0) đều là tường chặn -> không thể tới (1,1), trả về -1."
            }
        ],
        "hidden_tests": [
            {
                "input": {
                    "grid": [
                        [0, 0, 0, 0],
                        [0, 1, 1, 0],
                        [0, 0, 0, 0]
                    ]
                },
                "stdin": "3 4\n0 0 0 0\n0 1 1 0\n0 0 0 0\n",
                "expected": 5,
                "expected_stdout": "5"
            },
            {
                "input": {
                    "grid": [
                        [0, 1, 0],
                        [0, 1, 0],
                        [0, 0, 0]
                    ]
                },
                "stdin": "3 3\n0 1 0\n0 1 0\n0 0 0\n",
                "expected": 4,
                "expected_stdout": "4"
            },
            {
                "input": {
                    "grid": [
                        [1, 0],
                        [0, 0]
                    ]
                },
                "stdin": "2 2\n1 0\n0 0\n",
                "expected": -1,
                "expected_stdout": "-1"
            },
            {
                "input": {
                    "grid": [
                        [0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0]
                    ]
                },
                "stdin": "5 5\n0 0 0 0 0\n1 1 1 1 0\n0 0 0 0 0\n0 1 1 1 1\n0 0 0 0 0\n",
                "expected": 16,
                "expected_stdout": "16"
            },
            {
                "input": {
                    "grid": [[0]]
                },
                "stdin": "1 1\n0\n",
                "expected": 0,
                "expected_stdout": "0"
            }
        ]
    },
    {
        "id": "boss_6_knapsack_dp",
        "stage": 6,
        "problem_code": "KNAPSACK",
        "boss_name": "GIÁO SƯ EINSTEIN — TRÙM CUỐI",
        "boss_title": "Bậc Thầy Tối Ưu Hóa (Final Boss)",
        "topic": "Tối đa hóa giá trị túi đồ",
        "contest_name": "THỬ THÁCH LẬP TRÌNH — BÀI 6 (TRÙM CUỐI)",
        "file_py": "knapsack.py",
        "file_cpp": "knapsack.cpp",
        "time_limit": "1.0s (C++) / 2.0s (Python)",
        "memory_limit": "256 MB",
        "io_mode": "stdin/stdout hoặc hàm def solve(weights, values, capacity)",
        "max_hp": 1000,
        "theme_color": (180, 115, 10),
        "boss_shape": "einstein",
        "boss_image": "assets/boss_final.jpg",
        "description": (
            "[ĐỀ BÀI]:\n"
            "Cho N món vật phẩm. Món thứ i có trọng lượng W_i và giá trị V_i.\n"
            "Một chiếc túi có sức chứa tối đa là C đơn vị trọng lượng. Mỗi món chỉ được chọn lấy 1 lần hoặc bỏ qua.\n"
            "Hãy tìm tổng giá trị lớn nhất có thể mang theo mà tổng trọng lượng không vượt quá C.\n"
            "\n"
            "[DỮ LIỆU VÀO & RA]:\n"
            "- Cách 1 (Standard I/O - C++ / Python script):\n"
            "  + Input (stdin): Dòng 1 chứa N và C. Dòng 2 chứa N trọng lượng W_i. Dòng 3 chứa N giá trị V_i.\n"
            "  + Output (stdout): In ra một số nguyên duy nhất là tổng giá trị tối ưu.\n"
            "- Cách 2 (Hàm Python): Định nghĩa hàm def solve(weights, values, capacity) trả về số nguyên.\n"
            "\n"
            "[RÀNG BUỘC]:\n"
            "- 1 <= N <= 1000; 1 <= C <= 2000; 1 <= W_i, V_i <= 10^4."
        ),
        "input_format": "solve(weights: list[int], values: list[int], capacity: int) -> int | stdin: Dòng 1: N C; Dòng 2: N weights; Dòng 3: N values",
        "output_format": "Trả về số nguyên tổng giá trị lớn nhất hoặc in ra stdout",
        "constraints": "1 <= N <= 1000, 1 <= C <= 2000, 1 <= W_i, V_i <= 10^4",
        "sample_tests": [
            {
                "input": {"weights": [1, 2, 3], "values": [6, 10, 12], "capacity": 5},
                "stdin": "3 5\n1 2 3\n6 10 12\n",
                "expected": 22,
                "expected_stdout": "22",
                "explanation": "Chọn món 2 (w=2, v=10) và món 3 (w=3, v=12): Tổng trọng lượng 5 <= 5, Giá trị = 22."
            },
            {
                "input": {"weights": [4, 5, 1], "values": [1, 2, 3], "capacity": 4},
                "stdin": "3 4\n4 5 1\n1 2 3\n",
                "expected": 3,
                "expected_stdout": "3",
                "explanation": "Chọn món 3 (w=1, v=3): Giá trị đạt 3."
            }
        ],
        "hidden_tests": [
            {"input": {"weights": [2, 3, 4, 5], "values": [3, 4, 5, 6], "capacity": 5}, "stdin": "4 5\n2 3 4 5\n3 4 5 6\n", "expected": 7, "expected_stdout": "7"},
            {"input": {"weights": [10, 20, 30], "values": [60, 100, 120], "capacity": 50}, "stdin": "3 50\n10 20 30\n60 100 120\n", "expected": 220, "expected_stdout": "220"},
            {"input": {"weights": [5, 10, 15], "values": [10, 20, 30], "capacity": 4}, "stdin": "3 4\n5 10 15\n10 20 30\n", "expected": 0, "expected_stdout": "0"},
            {"input": {"weights": [3, 2, 1], "values": [5, 3, 2], "capacity": 5}, "stdin": "3 5\n3 2 1\n5 3 2\n", "expected": 8, "expected_stdout": "8"},
            {"input": {"weights": [1, 3, 4, 5], "values": [1, 4, 5, 7], "capacity": 7}, "stdin": "4 7\n1 3 4 5\n1 4 5 7\n", "expected": 9, "expected_stdout": "9"},
            {"input": {"weights": [6, 2, 3, 2, 3, 1], "values": [10, 4, 8, 3, 6, 2], "capacity": 10}, "stdin": "6 10\n6 2 3 2 3 1\n10 4 8 3 6 2\n", "expected": 21, "expected_stdout": "21"}
        ]
    }
]


def get_boss_problem(stage_or_id):
    """Retrieve boss problem by stage number (1..6) or ID."""
    if isinstance(stage_or_id, int):
        for p in DSA_BOSS_PROBLEMS:
            if p["stage"] == stage_or_id:
                return p
        return DSA_BOSS_PROBLEMS[0]
    for p in DSA_BOSS_PROBLEMS:
        if p["id"] == stage_or_id:
            return p
    return DSA_BOSS_PROBLEMS[0]

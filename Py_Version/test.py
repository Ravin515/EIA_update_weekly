import msvcrt
import sys
def detect_keys():
    print("按Enter键继续，按Esc键直接退出")
    while True:
        key = msvcrt.getch()
        if key == b'\r':  # Enter key is represented by b'\r'
            print("\nEnter key detected.")
        elif key == b'\x1b':  # ESC key is represented by b'\x1b'
            print("\n您已退出！")
            sys.exit(0)
        else:
            print("按Enter键继续，按Esc键直接退出")

detect_keys()

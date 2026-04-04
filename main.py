import sys
import os

# 添加src目录到sys.path，使 from the_evil.modules.xxx 可以工作
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from the_evil.the_evil import main

if __name__ == "__main__":
    main()

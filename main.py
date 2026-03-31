import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "the_evil"))

from the_evil import main

if __name__ == "__main__":
    main()

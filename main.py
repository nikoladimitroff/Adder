from time import sleep
from importlib import import_module
import sys


def main():
    if len(sys.argv) == 1:
        print("Missing demo argument")
        import_module("demos.snake")
    else:
        import_module("demos." + sys.argv[1])


if __name__ == "__main__":
    main()

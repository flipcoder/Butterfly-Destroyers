#!/usr/bin/python
import sys
from .app import *

def main():
    return App()()

if __name__ == '__main__':
    sys.exit(main() or 0)


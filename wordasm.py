#!/usr/bin/python3
import sys
from codetypes import *
import argparse
from importlib.machinery import SourceFileLoader
import importlib.util

def assembleWords(code: list[Code], out = sys.stdout.buffer):
    """ Assembles a List of Code objects to the target file. """
    for c in code:
        match c:
            case Word(v):
                if -2**31 <= v <= 2**32 - 1:
                    out.write(bytes((v >> i*8) & 0xff for i in (0, 1, 2, 3)))
                else:
                    raise Exception("Word({0}) is out of range".format(v))

if __name__ == "__main__":
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(  ), os.O_BINARY)

    parser = argparse.ArgumentParser(
                    prog="wordasm",
                    description="Assembles a sequence of Word objects")
    parser.add_argument("filename")
    args = parser.parse_args()
    
    spec = importlib.util.spec_from_file_location("code", args.filename)
    code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code)
    assembleWords(code.CODE) 

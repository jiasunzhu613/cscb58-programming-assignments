#!/usr/bin/python3
import sys
from codetypes import *
from wordasm import *

def lowerAssemblyCode(code: list[AssemblyCode]) -> list[Word]:
    """ Lowers away AssemblyCode instructions. """
    return code

def assembleCode(code: list[AssemblyCode], out = sys.stdout.buffer):
    """ Assembles a List of AssemblyCode objects to the target file. """
    assembleWords(lowerAssemblyCode(code))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="labelasm",
                    description="Assembles a sequence of ssemblyCode objects")
    parser.add_argument("filename")
    args = parser.parse_args()
    
    spec = importlib.util.spec_from_file_location("code", args.filename)
    code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code)
    assembleCode(code.CODE) 

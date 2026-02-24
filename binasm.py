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

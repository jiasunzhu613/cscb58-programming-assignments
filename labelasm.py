
#!/usr/bin/python3
import sys
from codetypes import *
from wordasm import *

def eliminateLabels(code: list[LabeledAssemblyCode]) -> tuple[list[AssemblyCode], dict[string, int]]:
    """ Lowers away LabeledAssemblyCode instructions. Returns a tuple of AssemblyCode and
        a dictionary mapping label definitions to addresses."""
    return (code, {})

def assembleCode(code: list[LabeledAssemblyCode], out = sys.stdout.buffer):
    """ Assembles a List of LabeledAssemblyCode objects to the target file. """
    newCode, labels = eliminateLabels(code)
    for (label, location) in labels:
        print("label {0} => {1}".format(label, location), file = sys.stderr)

    assembleWords(lowerAssemblyCode(newCode))

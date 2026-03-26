
#!/usr/bin/python3
import sys
from codetypes import *
from wordasm import *
from binasm import *
from typing import Dict

def eliminateLabels(code: list[LabeledAssemblyCode]) -> tuple[list[AssemblyCode], Dict[str, int]]:
    """ Lowers away LabeledAssemblyCode instructions. Returns a tuple of AssemblyCode and
        a dictionary mapping label definitions to addresses."""
    # find all labeled assembly code first
    # put them into dictionary mapped to the memory index they are present at!
    label_mapping = {}
    index = 0
    for instruction in code:
        if isinstance(instruction, Label):
            label_mapping[instruction.label] = index
        else:
            index += 1
    
    LabeledAssemblyCode.label_mapping = label_mapping

    index = 0
    newCode = []
    for instruction in code:
        # We do not assemble labels into final binary
        if isinstance(instruction, Label):
            continue

        print("inst", instruction, index, file=sys.stderr)
        if isinstance(instruction, LabeledAssemblyCode):
            newCode.append(instruction.resolve_label(index))
        elif isinstance(instruction, B) or isinstance(instruction, Bl) or isinstance(instruction, Mov):
            instruction.resolve_label(index)
            newCode.append(instruction)
        else:
            newCode.append(instruction)
            
        index += 1

    print("New code:", newCode, file=sys.stderr)
    print("Label mappings:", label_mapping, file=sys.stderr)        
    return (newCode, label_mapping)

def assembleCode(code: list[LabeledAssemblyCode], out = sys.stdout.buffer):
    """ Assembles a List of LabeledAssemblyCode objects to the target file. """
    newCode, labels = eliminateLabels(code)
    for label in labels:
        print("label {0} => {1}".format(label, labels[label]), file=sys.stderr)

    assembleWords(lowerAssemblyCode(newCode), out)

if __name__ == "__main__":
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(  ), os.O_BINARY)

    parser = argparse.ArgumentParser(
                    prog="labelasm",
                    description="Assembles a sequence of LabeledAssemblyCode objects")
    parser.add_argument("filename")
    args = parser.parse_args()
    
    spec = importlib.util.spec_from_file_location("code", args.filename)
    code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code)
    assembleCode(code.CODE) 

from dataclasses import dataclass


@dataclass(eq=False)
class LValue:
    pass


@dataclass(eq=False)
class VarTarget(LValue):
    name: str


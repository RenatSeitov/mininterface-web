from dataclasses import dataclass
from mininterface import run

from marimointerface import MarimoInterface

@dataclass
class NestedEnv:
    another_number: int = 7

@dataclass
class Env:
    nested_config: NestedEnv
    mandatory_str: str
    my_number: int | None = None
    my_string: str = "Hello"
    my_flag: bool = False
    my_validated: str = "hello"

with run(Env, interface=MarimoInterface, title="Demo") as m:
    print("Initial:", m.env)
    m.form()
    print("After form call (still old in this line):", m.env)

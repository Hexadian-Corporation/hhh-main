from dataclasses import dataclass


@dataclass
class Commodity:
    id: str | None = None
    name: str = ""
    code: str = ""

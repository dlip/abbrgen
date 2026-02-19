from abc import ABC, abstractmethod


class Keyboard(ABC):
    @abstractmethod
    def __init__(self, layout: str) -> None:
        pass

    @abstractmethod
    def get_layouts(self) -> list[str]:
        pass

    @abstractmethod
    def score(self, abbr: str) -> int:
        pass

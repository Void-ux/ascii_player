from typing import Iterable, Protocol, Any

__all__ = ('mean')


class Summable(Protocol):
    def __add__(self) -> Any:
        ...


def mean(data: Iterable[Summable]) -> float:
    return sum(data) / len(data)

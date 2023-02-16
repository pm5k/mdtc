from typing import Iterable

import pytest

from mdtc.singleton import Singleton


@pytest.fixture()
def get_foo() -> Iterable[tuple[Singleton, ...]]:
    class Foo(Singleton):
        foo: str = "bar"

    f1, f2 = Foo(), Foo()

    yield f1, f2
    f1.clear_instance()


def test_singleton_hash(get_foo: Iterable[tuple[Singleton, ...]]) -> None:
    """Test that a class implementing singleton instantiated twice won't share a hash."""
    inst_1, inst_2 = get_foo

    assert inst_1.__hash__() == inst_2.__hash__()


def test_singleton_props(get_foo: Iterable[tuple[Singleton, ...]]) -> None:
    """Test that modifying one singleton instance's props modifies the other's."""
    inst_1, inst_2 = get_foo

    inst_2.foo = "baz"  # type: ignore

    assert inst_1.foo == inst_2.foo  # type: ignore


def test_singleton_method_super() -> None:
    """Test that overwriting or super on Singleton works as intended"""

    # FIXME: this could be more useful..

    class Foo(Singleton):
        def __init__(self, bar: int) -> None:
            self.bar = bar

    class Bar(Singleton):
        def __init__(self, bar: int) -> None:
            super(Singleton, self).__init__()
            self.bar = bar

    foo = Foo(10)
    bar = Bar(20)

    assert foo.bar == 10
    assert bar.bar == 20

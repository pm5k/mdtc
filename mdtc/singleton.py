"""
MDTC Singleton module.
"""
from typing import Any


class Singleton:
    """
    Simplistic singleton-pattern class to inherit from.

    Best used for when you require only a single instance of a specific class
    to ever be allowed to exist in your program.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> "Singleton":
        """
        Intercept the `__new__` call and return an existing instance of this class instead.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

    @classmethod
    def clear_instance(cls) -> None:
        """Destroys current instance and re-sets the singleton."""
        del cls.instance

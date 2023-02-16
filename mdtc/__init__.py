# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


"""
## A model-driven singleton for storing TOML configuration.

Defines a Config class which is to be used for inheriting from.
In order to maintain a single configuration instance across your entire application state,
this class will enforce a singleton pattern which ensures that multiple instantiations
of the parent class which inherits from Config will result in the same class
instance.

Moreover, it allows the user to define the structure of their configuration via models,
which, out of the box - can be classes, dataclasses or Pydantic models.
Practically anything that can be instantiated and implements attribute getters and setters
should work as a configuration definition.
"""

import tomllib
from functools import reduce
from pathlib import Path
from typing import Any, Callable, get_type_hints

from mdtc.errors import (
    ConfigAttributeError,
    FrozenConfigException,
    TOMLKeyNotFoundError,
)
from mdtc.singleton import Singleton


class Config(Singleton):
    """
    Ensures that only on instance of your configuration is present in your application.

    At the same time, it enforces a pattern of defining your configuration via model-driven
    approach, where each TOML key is a pre-defined and pre-typed model of your configuration.
    """

    __isfrozen: bool = False
    __config_file: Path

    def __init__(self, config_file: str) -> None:
        """
        Initialise the configuration class using a file path and models.

        Args:
            config_file (str): The path to your `toml` configuration file.

        Raises:
            ConfigAttributeError: Raised when a model `_name` does not match the attribute
            defined inside your configuration class.
            TOMLKeyNotFoundError: Raised when a `_key` defined in the model is not found
            in the TOML configuration.
        """
        self.__config_file = Path(config_file)
        __conf = tomllib.loads(self.__config_file.read_text())
        # Because defining a model in the config for typing purposes does not define a
        # default value (and should not!), we use `get_type_hints` to retrieve this
        # from the child class and check against what the model would have defined.

        try:
            annotations = get_type_hints(self)
        except TypeError:
            raise Exception("No configs defined!")

        bases = [(name, cls_) for name, cls_ in annotations.items() if self.__implements_cfg(cls_)]

        if not bases:
            raise Exception("Configuration empty!")

        for name, base in bases:
            if name != base._name:
                raise ConfigAttributeError(
                    f"The model - `{base.__name__}` says it's TOML key name is - `{base._name}`,"
                    + f" but it has been declared as `{name}` inside `{self.__class__.__name__}`!"
                )

            if not (conf_dict := self.__get_cfg(base._key, __conf)):
                raise TOMLKeyNotFoundError(
                    f"The model - `{base.__name__}` asked to load a key - `{base._key}`"
                    + f" however `{config_file}` does not contain such a key!"
                )

            # Let the model throw own error on instantiation..
            self.__setattr__(base._name, base(**conf_dict))

        # Freeze the class instance
        self.__isfrozen = True

    def __setattr__(self, attr: str, value: Any) -> None:
        if self.__isfrozen:
            raise FrozenConfigException("Can't mutate the config!")
        super().__setattr__(attr, value)

    @staticmethod
    def __implements_cfg(class_: Any) -> bool:
        """Check if a given class uses `_key` and `_name` attributes as this class expects."""
        return hasattr(class_, "_key") and hasattr(class_, "_name")

    @staticmethod
    def __get_cfg(key: str, cfg: dict[str, Any]) -> Any:
        """
        Deep "get" from a n-depth dictionary using a TOML notation key.

        Args:
            key (str): The TOML key for where the configuration is housed.
            cfg (dict[str, Any]): The TOML dictionary parsed in from a file.

        Returns:
            Any: An applicable ANY-type value or None if key is not found.
        """

        reducer: Callable[..., Any] = lambda dict_, key: dict_.get(key) if dict_ else None
        return reduce(reducer, key.split("."), cfg)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            + f"hash={self.__hash__()},"
            + f" file='{self.__config_file.absolute()}')>"
        )

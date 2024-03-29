# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Type, TypeAlias

import pytest
import toml
from pydantic import BaseModel

from mdtc import Config
from mdtc.errors import (
    ConfigAttributeError,
    ConfigKeyNotFoundError,
    FrozenConfigException,
)

CONF_PATH: str = Path("tests/test.toml").read_text()
CONF_OBJ: dict[str, Any] = toml.loads(CONF_PATH)
CONF_NAME_KEY: str = "foo"
CONF_NAME_KEY_BAD: str = "coo"

#
# Preparatory Models
#


@dataclass
class DCConf:
    """Base dataclass-based model."""

    one: int
    two: list[str]
    three: dict[str, Any]

    _name: str = CONF_NAME_KEY
    _key: str = CONF_NAME_KEY


@dataclass
class DCConfMismatched:
    """Dataclass-based model which carries names that raise TOML/Attr errors."""

    one: int
    two: list[str]
    three: dict[str, Any]

    _name: str = CONF_NAME_KEY_BAD
    _key: str = CONF_NAME_KEY_BAD


class PDConf(BaseModel):
    """Base pydantic-based model."""

    _name: str = CONF_NAME_KEY
    _key: str = CONF_NAME_KEY

    one: int
    two: list[str]
    three: dict[str, Any]


class PDConfMismatched(BaseModel):
    """Pydantic-based model which carries names that raise TOML/Attr errors."""

    _name: str = CONF_NAME_KEY_BAD
    _key: str = CONF_NAME_KEY_BAD

    one: int
    two: list[str]
    three: dict[str, Any]


#
# Test Classes
#


class ConfigDC(Config):
    """Dataclass-based config"""

    foo: DCConf


class ConfigPD(Config):
    """Pydantic-based config"""

    foo: PDConf


# This will not match the model name and raise a model/conf mismatch error


class ConfigDCMismatchedFoo(Config):
    """Dataclass-based config which carries a model that raise TOML/Attr errors."""

    foo: DCConfMismatched


class ConfigPDMismatchedFoo(Config):
    """Pydantic-based config which carries a model that raise TOML/Attr errors."""

    foo: PDConfMismatched


# This will match the model, but not the config, raising the TOML attr error


class ConfigDCMismatchedCoo(Config):
    """Dataclass-based config which carries a model that raise TOML/Attr errors."""

    coo: DCConfMismatched


class ConfigPDMismatchedCoo(Config):
    """Pydantic-based config which carries a model that raise TOML/Attr errors."""

    coo: PDConfMismatched


RegularConfs: TypeAlias = tuple[ConfigDC, ConfigPD]
Mismatches: TypeAlias = tuple[
    Type[ConfigDCMismatchedFoo],
    Type[ConfigPDMismatchedFoo],
    Type[ConfigDCMismatchedCoo],
    Type[ConfigPDMismatchedCoo],
]
ConfigFixture: TypeAlias = Generator[tuple[RegularConfs, Mismatches], None, None]

#
# Fixtures
#


@pytest.fixture
def config_fixture() -> ConfigFixture:
    """
    Basic fixture returning a tuple of configs and uninstantiated mismatch configs.

    It also ensures that each test using this will re-set the singleton properly,
    before another test run begins.
    """

    regular: RegularConfs = (ConfigDC(CONF_OBJ), ConfigPD(CONF_OBJ))
    mismatch: Mismatches = (
        ConfigDCMismatchedFoo,
        ConfigPDMismatchedFoo,
        ConfigDCMismatchedCoo,
        ConfigPDMismatchedCoo,
    )

    yield (regular, mismatch)

    [cl.clear_instance() for cl in regular]


#
# Tests
#


def test_cfg_as_expected(config_fixture: ConfigFixture) -> None:
    """Test configuration instantiates and produces expected attributes."""
    regular_configs, _ = config_fixture
    dcconf = regular_configs[0]
    assert dcconf.foo.one == 1  # type: ignore
    assert dcconf.foo.two == ["one", "two"]  # type: ignore
    assert dcconf.foo.three == {"key": 3}  # type: ignore


def test_frozen_configs_raise_error(config_fixture: ConfigFixture) -> None:
    """
    Test that trying to reassign the config model inside the Config class raises.
    """
    regular_configs, _ = config_fixture
    dcconf = regular_configs[0]

    with pytest.raises(FrozenConfigException):
        dcconf.foo = 22  # type: ignore


def test_cfg_attr_mismatch(config_fixture: ConfigFixture) -> None:
    """
    Perform a sequential Dataclass/Pydantic model instantiation,
    then try to initialise the config when:

    1: Config attr does not match model name.
    2: Model key does not match any keys in config dict.
    """

    # Sequential test
    # First two should raise Model error last two should raise config key error..
    _, mismatches = config_fixture

    for mismatch in mismatches[:2]:
        with pytest.raises(ConfigAttributeError):
            mismatch(CONF_OBJ)  # type: ignore

    for mismatch in mismatches[2:]:
        with pytest.raises(ConfigKeyNotFoundError):
            mismatch(CONF_OBJ)  # type: ignore

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


class ConfigAttributeError(Exception):
    """Proxy exception for Attribute Errors inside the MDTC Singleton."""


class TOMLKeyNotFoundError(Exception):
    """Proxy exception for TOML Key Errors inside the MDTC Singleton."""


class FrozenConfigException(Exception):
    """Proxy exception for immutablility raises."""

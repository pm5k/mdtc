class ConfigAttributeError(Exception):
    """Proxy exception for Attribute Errors inside the MDTC Singleton."""


class TOMLKeyNotFoundError(Exception):
    """Proxy exception for TOML Key Errors inside the MDTC Singleton."""


class FrozenConfigException(Exception):
    """Proxy exception for immutablility raises."""

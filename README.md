# Readme

MDTC - Model-driven TOML Configuration.

A lightweight config singleton meant for storing your application's config state no matter where or how many times it is instantiated.
You can pass this object around across your entire app and not worry about config mutations, unvalidated config values or lack of IDE completions.
Originally meant for use with TOML key/value-based configs, but any k/v object should work as long as it complies with the model.

The source documentation can be found [here](https://pm5k.github.io/mdtc/)

## What is MDTC for?

- Avoids having to use or chain `.get()` or retrieve config values via `cfg["foo"]["bar"]["baz"]`.
- Code-completion-friendly via model-driven approach.
- Custom configuration validation (either via Pydantic's interfaces or custom-built validators you define).
- Immutable config state support. The config itself is immutable by default - you cannot replace `config.foo` with another value, for instance.
- Supports nicer type hints instead of a huge TypeDict or another approach for a config dictionary loaded into Python.

## What MDTC is not for

- It is not meant to replace other methods of loading TOML or dict configs, it simply provides an alternative for housing your TOML config values.
- It is not meant as "less code". The guarantees it provides require a different implementation approach, and won't always result in less upfront code.
- Codebases using other approaches or small configs won't benefit from this approach as much.

## Dependencies

None, just the Python standard library.

## Examples

### Simple Configuration

```py title="main.py"
import tomllib # python3.11-only, use tomli for <=3.10

from dataclasses import dataclass
from mdtc import Config

@dataclass
class FooCfg:
    foo: str
    bar: str

    _name: str = "misc"
    _key: str = "config.misc"


class MyConf(Config):
    misc: FooCfg

cfg = """
[config.misc]
foo="bar"
bar="baz"
"""

toml = tomllib.loads(cfg)

config = MyConf(toml)
```

### Pydantic Models in your Configuration

```py title="main.py"
import tomllib # python3.11-only, use tomli for <=3.10

from pydantic import BaseModel
from mdtc import Config


class FooCfg(BaseModel):
    _name: str = "misc"
    _key: str = "config.misc"
    
    foo: str
    bar: str


class MyConf(Config):
    misc: FooCfg


cfg = """
[config.misc]
foo="bar"
bar="baz"
"""

toml = tomllib.loads(cfg)

config = MyConf(toml)
```

### Pydantic `dataclass` Example

```py title="main.py"
import tomllib # python3.11-only, use tomli for <=3.10

from pydantic import Field, validator
from pydantic.dataclasses import dataclass

from mdtc import Config


@dataclass
class FooCfg:
    foo: str
    bar: str = Field(title="A bar to get drinks in..")

    _name: str = "misc"
    _key: str = "config.misc"

    @validator("foo")
    def name_must_contain_space(cls, v):
        if " " in v:
            raise ValueError("must NOT contain a space!")
        return v.title()


class MyConf(Config):
    misc: FooCfg


cfg = """
[config.misc]
foo="bar"
bar="baz"
"""

toml = tomllib.loads(cfg)

config = MyConf(toml)
```

## Contributing

`Coming soon..`

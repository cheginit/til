# Setup `netrc` for using EarthData

Some web services, such as [EarthData](https://earthdata.nasa.gov/), require user
registration and personal token for giving access their database. The following snippet
creates a `~/.netrc` file based on the provided user and pass for a given URS.

```python
from netrc import netrc
from typing import Dict
from getpass import getpass
from pathlib import Path


def setup_urs_login(urs: str) -> None:
    prompts = {
        "login": "\n".join(
            [
                "Enter NASA EarthData Login Username",
                f"(or create an account at {urs}): ",
            ]
        ),
        "password": "Enter NASA EarthData Login Password: ",
    }

    netrc_file = Path.home().joinpath(".netrc")

    try:
        netrc(netrc_file).authenticators(urs)[1]
    except (FileNotFoundError, TypeError) as exc:
        user_data: Dict[str, str] = {}
        for p, msg in prompts.items():
            user_data[p] = getpass(prompt=msg)

        fmode = "w" if exc.__class__ == FileNotFoundError else "a"
        with open(netrc_file, fmode) as f:
            msg = f"machine {urs}\n"
            msg += "\n".join(f"{p} {m}" for p, m in user_data.items())
            f.write(msg)
    print(f"User-pass info successfully set for {urs}.")


if __name__ == "__main__":
    setup_urs_login("https://urs.earthdata.nasa.gov")
```

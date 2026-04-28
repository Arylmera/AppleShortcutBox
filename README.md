# Apple Shortcuts builder

Programmatic Apple Shortcut authoring in Python.

**Full docs:** [docs/README.md](docs/README.md)
**Skill (for Claude):** [docs/SKILL.md](docs/SKILL.md)

Built on top of [python-shortcuts](https://github.com/alexander-akhmetov/python-shortcuts) (see [docs/external-libraries.md](docs/external-libraries.md)).

Quickstart:

```bash
# One-time install
pip3 install --user shortcuts

# Generate a shortcut
python3 builders/hello-world.py

# Sign and import (macOS only)
bash docs/sign-all.sh
open signed/hello-world.shortcut
```

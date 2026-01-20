<div align = "center">

<h1><a href="https://2kabhishek.github.io/orgpy">orgpy</a></h1>

<a href="https://github.com/2KAbhishek/orgpy/blob/main/LICENSE">
<img alt="License" src="https://img.shields.io/github/license/2kabhishek/orgpy?style=flat&color=eee&label="> </a>

<a href="https://github.com/2KAbhishek/orgpy/graphs/contributors">
<img alt="People" src="https://img.shields.io/github/contributors/2kabhishek/orgpy?style=flat&color=ffaaf2&label=People"> </a>

<a href="https://github.com/2KAbhishek/orgpy/stargazers">
<img alt="Stars" src="https://img.shields.io/github/stars/2kabhishek/orgpy?style=flat&color=98c379&label=Stars"></a>

<a href="https://github.com/2KAbhishek/orgpy/network/members">
<img alt="Forks" src="https://img.shields.io/github/forks/2kabhishek/orgpy?style=flat&color=66a8e0&label=Forks"> </a>

<a href="https://github.com/2KAbhishek/orgpy/watchers">
<img alt="Watches" src="https://img.shields.io/github/watchers/2kabhishek/orgpy?style=flat&color=f5d08b&label=Watches"> </a>

<a href="https://github.com/2KAbhishek/orgpy/pulse">
<img alt="Last Updated" src="https://img.shields.io/github/last-commit/2kabhishek/orgpy?style=flat&color=e06c75&label="> </a>

<h3>Organize your digital mess 🗂️🗃️</h3>

</div>

orgpy is a `utility` that allows you to quickly organize your files in a predefined structure

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed the latest version of `python3`

## Installing orgpy

To install orgpy, follow these steps:

```bash
git clone https://github.com/2kabhishek/orgpy
cd orgpy
# Setup symlink, make sure target directory is added to PATH
ln -sfnv "$PWD/orgpy.py" ~/Applications/bin/orgpy
```

## Using orgpy

```bash
USAGE:
    orgpy [-h] [path] [--dry-run] [-c CONFIG_FILE] [--config-path]

Organize your digital mess.

positional arguments:
  path                  The directory path to organize. [Default: current working directory]

options:
  -h, --help            show this help message and exit
  --dry-run             Preview changes without actually moving files.
  -c, --config CONFIG_FILE
                        Path to custom configuration file.
  --config-path         Show configuration file path and exit.

Visit github.com/2KAbhishek/orgpy for more.

EXAMPLE:
orgpy ~/Downloads     # Organizes your downloads directory
orgpy ~/Desktop --dry-run  # Preview what would be organized in desktop
```

### Configuration

orgpy automatically creates a config file at `~/.config/orgpy.json` on first run with default file categories.
You can customize this file to add your own categories or modify existing ones.

```bash
# Show config file location
orgpy --config-path

# Use custom config file
orgpy --config /path/to/custom/config.json
```

### Running Tests

The project includes a comprehensive test suite with **zero external dependencies** (uses only Python's built-in `unittest`):

```bash
# Run all tests
python3 tests/test_orgpy.py

# Or run with module discovery
python3 -m unittest discover tests -v
```

Hit the ⭐ button if you found this useful.

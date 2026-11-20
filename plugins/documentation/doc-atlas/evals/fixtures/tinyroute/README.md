# TinyRoute

Print a local greeting from the command line. TinyRoute takes one name and writes a greeting to standard output.

## Get started

Use Python 3.10 or newer. From the repository root in a POSIX shell, run directly from this checkout:

```sh
PYTHONPATH=src python -m tinyroute --name Ada
```

Expected output:

```text
Hello, Ada!
```

`--name` is required. Replace `Ada` with the name you want to greet; quote names that contain spaces.

## Explore the CLI

Show the available options:

```sh
PYTHONPATH=src python -m tinyroute --help
```

For the implementation, read the [argument parser and greeting function](src/tinyroute/cli.py).

## Check the behavior

Run the tests from the repository root:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

The [CLI tests](tests/test_cli.py) cover the greeting, the required name, and rejection of unsupported options.

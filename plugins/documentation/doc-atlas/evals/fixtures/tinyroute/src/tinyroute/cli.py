"""A deliberately small, dependency-free CLI contract."""

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tinyroute",
        description="Print a local greeting for a name.",
    )
    parser.add_argument("--name", required=True, help="Name to include in the greeting")
    args = parser.parse_args(argv)
    print(f"Hello, {args.name}!")
    return 0

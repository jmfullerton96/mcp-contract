"""mcpc CLI entry point."""

from __future__ import annotations

import argparse
import sys

from mcpc import __version__
from mcpc.init import TEMPLATES, init_bundle
from mcpc.validate import validate_bundle


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mcpc",
        description="CLI for the MCP Contract specification.",
    )
    parser.add_argument(
        "--version", action="version", version=f"mcpc {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # -- validate --
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an MCP Contract bundle.",
        description=(
            "Validates the manifest against the schema, checks that all "
            "provides/consumes contracts are satisfied, and verifies that "
            "referenced files exist."
        ),
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the bundle directory (default: current directory).",
    )
    validate_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print errors, suppress informational output.",
    )

    # -- init --
    init_parser = subparsers.add_parser(
        "init",
        help="Scaffold a new MCP Contract bundle.",
        description="Creates a new bundle directory with manifest and starter files.",
    )
    init_parser.add_argument(
        "name",
        help="Bundle name (lowercase, hyphens only).",
    )
    init_parser.add_argument(
        "--path",
        default=".",
        help="Parent directory for the new bundle (default: current directory).",
    )
    init_parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default="full",
        help="Bundle template (default: full).",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "validate":
        ok = validate_bundle(args.path, quiet=args.quiet)
        sys.exit(0 if ok else 1)

    if args.command == "init":
        ok = init_bundle(args.name, args.path, args.template)
        sys.exit(0 if ok else 1)

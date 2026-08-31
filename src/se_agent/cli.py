"""se-agent command-line interface (REQ-V1, REQ-V2; design D2/D3/D5).

Exit codes (D5):
- 0   success (every planned write done / version printed);
- 1   operational failure (invalid destination, preflight/safety error,
      collision abort, mid-write failure, version metadata not installed);
- 2   usage error (argparse: unknown flag, invalid --harness, missing --target);
- 130 KeyboardInterrupt (zero-writes guarantee holds only before the first write).

Parse errors precede every filesystem access (REQ-V2): argument parsing never
touches the filesystem, so a usage error is always a zero-write outcome.
"""

from __future__ import annotations

import argparse
import enum
import importlib.metadata
import sys
from collections.abc import Sequence

from se_agent.init_flow import run_init


class ExitCode(enum.IntEnum):
    """Single mapping of CLI exit codes (D5).

    0 success (every planned write done / version printed); 1 operational
    failure (invalid destination, preflight/safety error, collision abort,
    mid-write failure, version metadata not installed); 2 usage error
    (argparse: unknown flag, invalid --harness, missing --target); 130
    KeyboardInterrupt (zero-writes guarantee holds only before the first write).
    """

    OK = 0
    OPERATIONAL_ERROR = 1
    USAGE_ERROR = 2
    INTERRUPTED = 130

#: The MVP accepts exactly one harness value (REQ-V2).
HARNESS_CHOICES = ("codex",)


def _print_version() -> None:
    """Print the installed SemVer bare (no `v` prefix) to stdout (REQ-V1).

    On `PackageNotFoundError`, exits 1 with an explicit message naming the
    distribution. A fallback dev string is never printed (D2).
    """
    try:
        version = importlib.metadata.version("se-agent")
    except importlib.metadata.PackageNotFoundError:
        print(
            "se-agent: error: package 'se-agent' is not installed; "
            "cannot determine version (no fallback version is used).",
            file=sys.stderr,
        )
        raise SystemExit(ExitCode.OPERATIONAL_ERROR) from None
    print(version)


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse surface (D3): top-level --version + `init` subcommand."""
    parser = argparse.ArgumentParser(
        prog="se-agent",
        description=(
            "One-shot Codex scaffolder: installs the declared payload into a "
            "target project, transfers ownership, and terminates."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="print the installed package version (bare SemVer) and exit",
    )
    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser(
        "init",
        help="install the payload into --target",
    )
    init_parser.add_argument(
        "--harness",
        choices=HARNESS_CHOICES,
        required=True,
        help="target harness (only 'codex' is supported in the MVP)",
    )
    init_parser.add_argument(
        "--target",
        required=True,
        help="destination directory that receives the payload",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite colliding write-set paths without prompting",
    )
    return parser


def _run_init(args: argparse.Namespace) -> int:
    """Parse-validated `init` entry point (design §4 steps 3–9 via init_flow).

    `--force` is handed to the collision step only; it never relaxes the
    safety preflight (REQ-W4, design §5).
    """
    return run_init(args.target, force=args.force)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Parse errors raise SystemExit(2) from argparse (D3/D5).

    KeyboardInterrupt maps to exit 130; the zero-writes guarantee holds only
    if the interrupt precedes the first write (D5, documented limitation).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        _print_version()
        return ExitCode.OK
    if args.command == "init":
        try:
            return _run_init(args)
        except KeyboardInterrupt:
            print(
                "se-agent: error: interrupted; zero writes only if the "
                "interrupt happened before the first write.",
                file=sys.stderr,
            )
            return ExitCode.INTERRUPTED
    parser.error("a command is required (use 'init' or '--version')")  # exits 2

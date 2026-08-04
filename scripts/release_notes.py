"""Extract one version section from the project changelog."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_release_notes(changelog: str, version: str) -> str:
    """Return exactly one Markdown release section for ``version``.

    Args:
        changelog: Complete Keep-a-Changelog-style Markdown text.
        version: Version number without a leading tag prefix.

    Returns:
        The selected section with one trailing newline.

    Raises:
        ValueError: When the changelog contains zero or multiple matching headings.
    """
    heading = re.compile(rf"^## \[{re.escape(version)}\](?:\s+-\s+.+)?\s*$", re.MULTILINE)
    matches = list(heading.finditer(changelog))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one changelog section for version {version}")
    start = matches[0].start()
    tail = changelog[matches[0].end() :]
    following = re.search(r"^## \[", tail, re.MULTILINE)
    end = matches[0].end() + following.start() if following is not None else len(changelog)
    return changelog[start:end].strip() + "\n"


def main() -> int:
    """Extract release notes from a changelog and print or write them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    notes = extract_release_notes(
        arguments.changelog.read_text(encoding="utf-8"),
        arguments.version,
    )
    if arguments.output is None:
        print(notes, end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(notes, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

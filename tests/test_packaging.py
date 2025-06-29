"""
Shamelessly inspired from https://github.com/pypa/twine/blob/main/twine/commands/check.py
"""
import io
import re
from importlib.metadata import metadata

from readme_renderer.rst import render

# Regular expression used to capture and reformat docutils warnings into
# something that a human can understand. This is loosely borrowed from
# Sphinx: https://github.com/sphinx-doc/sphinx/blob
# /c35eb6fade7a3b4a6de4183d1dd4196f04a5edaf/sphinx/util/docutils.py#L199
_REPORT_RE = re.compile(
    r"^<string>:(?P<line>(?:\d+)?): "
    r"\((?P<level>DEBUG|INFO|WARNING|ERROR|SEVERE)/(\d+)?\) "
    r"(?P<message>.*)",
    re.DOTALL | re.MULTILINE,
)


class _WarningStream:
    def __init__(self) -> None:
        self.output = io.StringIO()

    def write(self, text: str) -> None:
        matched = _REPORT_RE.search(text)

        if not matched:
            self.output.write(text)
            return

        self.output.write(
            "line {line}: {level_text}: {message}\n".format(
                level_text=matched.group("level").capitalize(),
                line=matched.group("line"),
                message=matched.group("message").rstrip("\r\n"),
            )
        )

    def __str__(self) -> str:
        return self.output.getvalue()


def test_check_pypi_rendering():
    lines = metadata("marisa-trie").get("Summary", "").splitlines()
    description = lines.pop(0) + "\n"
    description += "\n".join(l[8:] for l in lines)

    warnings = _WarningStream()
    rendering = render(description, stream=warnings)
    print(description)
    print(warnings)
    assert not str(warnings)
    assert rendering is not None

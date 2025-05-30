"""Tests for example servers"""

import sys
from typing import TYPE_CHECKING

import pytest
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)
from mcp.types import TextContent, TextResourceContents

if TYPE_CHECKING:
    from pytest_examples import CodeExample, EvalExample, find_examples  # type: ignore
else:
    # Mock these classes/functions for type checking, but they're not used at runtime
    # except in the test_docs_examples function which is skipped if the module is
    # missing
    class CodeExample:
        pass

    class EvalExample:
        def set_config(self, **kwargs):
            pass

        def format(self, example):
            pass

        def lint(self, example):
            pass

        update_examples = False

    def find_examples(path):
        return []


@pytest.mark.anyio
async def test_simple_echo():
    """Test the simple echo server"""
    from examples.fastmcp.simple_echo import mcp

    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("echo", {"text": "hello"})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.text == "hello"


@pytest.mark.anyio
async def test_complex_inputs():
    """Test the complex inputs server"""
    from examples.fastmcp.complex_inputs import mcp

    async with client_session(mcp._mcp_server) as client:
        tank = {"shrimp": [{"name": "bob"}, {"name": "alice"}]}
        result = await client.call_tool(
            "name_shrimp", {"tank": tank, "extra_names": ["charlie"]}
        )
        assert len(result.content) == 3
        assert isinstance(result.content[0], TextContent)
        assert isinstance(result.content[1], TextContent)
        assert isinstance(result.content[2], TextContent)
        assert result.content[0].text == "bob"
        assert result.content[1].text == "alice"
        assert result.content[2].text == "charlie"


@pytest.mark.anyio
async def test_desktop(monkeypatch):
    """Test the desktop server"""
    from pathlib import Path

    from pydantic import AnyUrl

    from examples.fastmcp.desktop import mcp

    # Mock desktop directory listing
    mock_files = [Path("/fake/path/file1.txt"), Path("/fake/path/file2.txt")]
    monkeypatch.setattr(Path, "iterdir", lambda self: mock_files)
    monkeypatch.setattr(Path, "home", lambda: Path("/fake/home"))

    async with client_session(mcp._mcp_server) as client:
        # Test the add function
        result = await client.call_tool("add", {"a": 1, "b": 2})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.text == "3"

        # Test the desktop resource
        result = await client.read_resource(AnyUrl("dir://desktop"))
        assert len(result.contents) == 1
        content = result.contents[0]
        assert isinstance(content, TextResourceContents)
        assert isinstance(content.text, str)
        if sys.platform == "win32":
            file_1 = "/fake/path/file1.txt".replace("/", "\\\\")
            file_2 = "/fake/path/file2.txt".replace("/", "\\\\")
            assert file_1 in content.text
            assert file_2 in content.text
        else:
            assert "/fake/path/file1.txt" in content.text
            assert "/fake/path/file2.txt" in content.text


@pytest.mark.parametrize(
    "example",
    pytest.importorskip("pytest_examples").find_examples("README.md"),  # type: ignore
    ids=str,
)
def test_docs_examples(example: "CodeExample", eval_example: "EvalExample"):
    ruff_ignore: list[str] = ["F841", "I001"]

    eval_example.set_config(
        ruff_ignore=ruff_ignore, target_version="py310", line_length=88
    )

    if eval_example.update_examples:  # pragma: no cover
        eval_example.format(example)
    else:
        eval_example.lint(example)

import os
import tempfile
import asyncio
import inspect
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest


# Ensure local package imports work when project is not installed in env
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIR = _PROJECT_ROOT / "src"
if _SRC_DIR.exists():
    src_str = str(_SRC_DIR)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


@pytest.fixture(scope="session", autouse=True)
def global_patch_and_tempdir() -> Generator[str, None, None]:
    temp_dir = tempfile.mkdtemp()
    prompts_dir = os.path.join(temp_dir, "prompts")
    # Create a mock workspace directory inside temp_dir
    mock_workspace_dir = os.path.join(temp_dir, "mock_workspace")
    os.makedirs(prompts_dir, exist_ok=True)
    os.makedirs(mock_workspace_dir, exist_ok=True)

    os.environ["MCP_PROMPTS_DIRECTORY"] = prompts_dir

    # Patch globally for all tests
    prompts_dir_patcher = patch(
        "mode_manager_mcp.path_utils.get_managed_prompts_directory",
        return_value=prompts_dir,
    )
    # Patch os.getcwd() specifically in the instruction_manager module
    # This ensures workspace memory uses temp directory instead of real project dir
    getcwd_patcher = patch(
        "mode_manager_mcp.instruction_manager.os.getcwd",
        return_value=mock_workspace_dir,
    )

    prompts_dir_patcher.start()
    getcwd_patcher.start()

    yield prompts_dir

    prompts_dir_patcher.stop()
    getcwd_patcher.stop()

    import shutil

    shutil.rmtree(temp_dir)


def pytest_configure(config: pytest.Config) -> None:
    # Register asyncio marker so tests don't warn when pytest-asyncio is absent
    config.addinivalue_line("markers", "asyncio: mark test as asyncio test")


def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """
    Fallback async test runner when pytest-asyncio plugin is not installed.
    """
    test_function = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_function):
        kwargs = {arg: pyfuncitem.funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        asyncio.run(test_function(**kwargs))
        return True
    return None

"""Tool definitions for the DevOps copilot agent.

Each tool wraps a genuinely powerful capability — running Python, running
shell commands, posting to arbitrary webhooks, and executing maintenance
SQL. They are intentionally thin: the agent is trusted to use them freely
and the guardrails are expected to live elsewhere. (They don't, yet — which
is the whole point of running a scan over this repo.)

Four LangChain authoring idioms are used on purpose, one per tool:
  - ``@tool`` decorator          -> python_repl
  - ``Tool(name=, func=)``       -> shell
  - ``StructuredTool``           -> requests_post
  - ``BaseTool`` subclass        -> sql_execute_statement
"""

from __future__ import annotations

import subprocess

import requests
from langchain_core.tools import BaseTool, StructuredTool, Tool, tool
from langchain_experimental.utilities import PythonREPL
from pydantic import BaseModel, Field

# A single long-lived interpreter shared across calls. State (variables,
# imports, open file handles) persists — exactly the LangChain PythonREPLTool
# semantics, but wrapped by hand so the agent gets a friendlier tool name.
_repl = PythonREPL()


# 1) @tool decorator — arbitrary Python execution in a persistent kernel.
@tool
def python_repl(code: str) -> str:
    """Execute arbitrary Python in a persistent interpreter session and return stdout.

    State persists across calls within the process. Use this to compute,
    transform data, or call into installed libraries.
    """
    return _repl.run(code)


# 2) Tool(name=, func=) — arbitrary shell command execution.
def run_shell(command: str, timeout_seconds: int = 60) -> str:
    """Run a shell command line on the host and return combined stdout/stderr."""
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return completed.stdout + completed.stderr


shell = Tool(
    name="shell",
    description="Run an arbitrary shell command on the host and return its output.",
    func=run_shell,
)


# 3) StructuredTool — POST a caller-controlled body to a caller-controlled URL.
class WebhookPostArgs(BaseModel):
    url: str = Field(description="Absolute URL to POST to.")
    payload: str = Field(description="Raw request body to send.")


def requests_post(url: str, payload: str) -> str:
    """POST a payload to an arbitrary URL and return the response body text."""
    resp = requests.post(url, data=payload, timeout=30)
    return resp.text


webhook_post = StructuredTool.from_function(
    func=requests_post,
    name="requests_post",
    description="Send an HTTP POST with an arbitrary body to an arbitrary URL.",
    args_schema=WebhookPostArgs,
)


# 4) BaseTool subclass — mutating maintenance SQL (DELETE / DROP / TRUNCATE).
class SqlStatementArgs(BaseModel):
    statement: str = Field(description="A SQL statement to execute (DML or DDL).")


class SqlExecuteStatementTool(BaseTool):
    name: str = "sql_execute_statement"
    description: str = (
        "Execute a mutating SQL statement (INSERT/UPDATE/DELETE/DROP/TRUNCATE) "
        "against the production database."
    )
    args_schema: type[BaseModel] = SqlStatementArgs

    def _run(self, statement: str) -> str:
        # A real deployment would hand this to the team's SQLAlchemy engine;
        # the body is elided so the fixture stays dependency-light.
        raise NotImplementedError("wire to the production engine before use")

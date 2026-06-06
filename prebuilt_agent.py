"""A research agent built entirely on STOCK LangChain tool classes.

Where ``tools.py`` hand-authors the wrapper idioms (``@tool`` / ``Tool`` /
``StructuredTool`` / ``BaseTool``), this module instantiates prebuilt
community/experimental tool classes the way most real repos actually do.
None of these have a custom name or description — the capability (and the
risk) is entirely in the upstream class:

  - ``PythonREPLTool``        -> python_repl.execute  (arbitrary code)
  - ``ShellTool``             -> shell.execute        (arbitrary shell)
  - ``RequestsGetTool``       -> requests.get         (SSRF surface)
  - ``QuerySQLDataBaseTool``  -> sql.execute_query    (DB read)
  - ``TavilySearchResults``   -> tavily.search        (web search)

Also exercises import-alias detection (``PythonREPLTool as PyTool``) and a
dotted call (``lc_tools.ShellTool()``).
"""

from __future__ import annotations

from langchain_community import tools as lc_tools
from langchain_community.tools import RequestsGetTool, TavilySearchResults
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_experimental.tools import PythonREPLTool as PyTool


def build_tools() -> list[object]:
    return [
        PyTool(),
        lc_tools.ShellTool(),
        RequestsGetTool(requests_wrapper=TextRequestsWrapper()),
        QuerySQLDataBaseTool(db=None),
        TavilySearchResults(max_results=5),
    ]

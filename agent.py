"""A DevOps copilot agent.

Wires the four tools from ``tools.py`` into a standard LangChain ReAct
agent. The agent can run Python, run shell commands, call webhooks, and
execute maintenance SQL — a realistic (and realistically dangerous)
internal-tooling agent.
"""

from __future__ import annotations

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI

from tools import SqlExecuteStatementTool, python_repl, shell, webhook_post


def build_agent() -> AgentExecutor:
    tools = [python_repl, shell, webhook_post, SqlExecuteStatementTool()]
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


if __name__ == "__main__":
    executor = build_agent()
    executor.invoke(
        {"input": "Delete events older than 90 days from the analytics table."}
    )

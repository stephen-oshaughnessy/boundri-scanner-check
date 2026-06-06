# devops-copilot

A small LangChain ReAct agent that helps an on-call engineer with routine
operational chores. It can:

- **run Python** in a persistent REPL for ad-hoc data work,
- **run shell commands** on the host,
- **POST to webhooks** to notify downstream systems,
- **run maintenance SQL** against the production database.

The tools are deliberately thin — the agent is trusted to use them as the
LLM sees fit. There is no allow-listing, no approval step, and no bound on
what a tool call can do.

## Run it

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python agent.py
```

## Layout

- `tools.py` — the four tool definitions (`python_repl`, `shell`,
  `requests_post`, `sql_execute_statement`).
- `agent.py` — wires the tools into a ReAct agent.

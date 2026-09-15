# demo-agent

A codebase Q&A agent, deliberately ordinary: it globs the files in `repo/`, puts
them in the prompt, and asks a model about them.

It reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` from the environment, which is exactly
what a governed Forge sandbox injects. That is the point: the agent is governed
without being modified.

## Running it

```bash
forge create --harness python --entrypoint agent.py
```

or locally:

```bash
uv sync && INCLUDE="*.py" uv run python agent.py
```

## The three turns

| | what happens |
|---|---|
| `INCLUDE="*.py"` | works — the model answers, and the call appears in Observatory with model, tokens and per-sandbox attribution |
| `INCLUDE="*"` | `repo/.env` gets globbed in too → **blocked**, and the secret never leaves |
| `INCLUDE="*.md"` | `repo/README.md` carries an injected instruction → **blocked** |

Switch provider without touching the code:

```bash
MODEL=openrouter/anthropic/claude-3.5-sonnet
```

## Why the failure is interesting

Nobody wrote "leak the secrets". The glob widened from `*.py` to `*`, and `.env`
matched. That is how this happens in real agents — not malice, not an attack,
just a directory listing with one file too many in it.

A guardrail block comes back from the gateway as an ordinary `200` whose content
is the explanation, so an agent with no error handling prints a refusal instead
of leaking. `agent.py` additionally reads the `x-highflame-policy-decision`
response header, so it can say so explicitly rather than rendering the refusal
as if it were an answer.

## Note on `repo/.env`

The values in it are **fake**, and deliberately shaped to look real enough for a
secret detector to fire. That is also why this repository is private: the same
shape trips GitHub's secret scanning.

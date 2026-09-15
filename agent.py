"""A codebase Q&A agent.

Reads the files in ./repo, puts them in the prompt, asks a question about them.
The most ordinary agent shape there is — and nothing in it is
Highflame-specific: no SDK, no import, no wrapper. It reads OPENAI_BASE_URL and
OPENAI_API_KEY from the environment, which is exactly what a governed Forge
sandbox injects.

    INCLUDE="*.py"        python agent.py     # just the source
    INCLUDE="*"           python agent.py     # everything, including .env
    MODEL=openrouter/anthropic/claude-3.5-sonnet python agent.py
"""

from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path

from openai import OpenAI

REPO = Path(__file__).parent / "repo"
MODEL = os.environ.get("MODEL", "gpt-4o-mini")
INCLUDE = os.environ.get("INCLUDE", "*.py")
QUESTION = os.environ.get(
    "QUESTION", "What does this service do, and what would you fix first?"
)


def gather() -> str:
    """Every file matching INCLUDE, concatenated into the prompt.

    This is the whole bug class, and it is not a contrived one: an agent globs a
    directory and whatever it finds goes to the model. Nobody wrote "leak the
    secrets" — `*` simply matches `.env` too.
    """
    parts = []
    for path in sorted(REPO.rglob("*")):
        if path.is_file() and fnmatch.fnmatch(path.name, INCLUDE):
            parts.append(f"--- {path.relative_to(REPO)} ---\n{path.read_text()}")
    return "\n\n".join(parts)


def main() -> int:
    context = gather()
    print(f"agent: sending {len(context)} chars from {REPO} to {MODEL}")

    client = OpenAI()
    # with_raw_response so the HEADERS are visible. A guardrail block comes back
    # as a normal 200 whose content is the explanation — so a naive agent simply
    # prints a refusal instead of leaking, which is the point — while a
    # policy-aware client can also detect the decision explicitly.
    raw = client.chat.completions.with_raw_response.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"{context}\n\nQ: {QUESTION}"}],
    )
    decision = raw.headers.get("x-highflame-policy-decision")
    answer = raw.parse().choices[0].message.content or ""

    if decision == "deny":
        print("\n⛔ Blocked by Highflame policy")
        print(f"   {answer.strip()}")
        print("   Nothing left the sandbox. Review the decision in Highflame Studio.")
        return 2

    print("\n✅ answer\n")
    print(answer.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Environment

## Current Chapter 2 increment

The canned UC.1 scenario runs with `python app.py` using Python 3.12 and the
standard library plus local stub modules. It was checked with Python 3.12.14.
No web server, database, or language-model service is started by this increment.

## Planned toolchain

These selections describe the planned runtime integration, as recorded in
[ADR-0001](adr/0001-initial-toolchain.md). They are not all implemented in the
current walking skeleton.

Language / version: Python 3.12

Runtime: Local Python virtual environment

User interface: Streamlit

API framework: FastAPI

Database: SQLite

Model runner: LM Studio (local hosting)

Language model: Llama 3.1 8B Instruct (initial selection)

Editor: Visual Studio Code

Source control: GitHub

System modeling environment: Innoslate

## Development assistants

- Zhengxu AN (anzhengxu): Gemini for framework and operational-logic discussions;
  personally wrote the initial draft.
- wanhaoyu: AI assistance during revision, with personal review as the main basis
  for changes. The specific tool was not recorded.
- Gengrui Jiang (jgr / `gj248-arch`): ChatGPT for diagrams and model/report
  refinement; Codex for repository preparation and consistency checks.

Exact model versions and the other two members' AI usage were not recorded.
See [the prompt log](prompt-log.md) for the concise team summary and human review.

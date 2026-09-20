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

- Gengrui Jiang (`gj248-arch`): Codex, used for the documentation and model/code
  alignment recorded in [the prompt log](prompt-log.md). The assistant model
  identifier was not recorded.
- The original team environment record listed ChatGPT without naming its
  individual users or model identifiers.
- Other members' individual assistant usage is not documented in this public
  record.

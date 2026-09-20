# ADR-0001: Initial Toolchain

Status: Accepted

## Context

DormFix requires a lightweight prototype architecture that supports a web-based user interface, a REST API, persistent maintenance-ticket storage, and configurable language-model assistance.

## Decision

The initial DormFix prototype will use:

- Python 3.12
- Streamlit for the user interface
- FastAPI for the REST API
- SQLite for ticket storage
- A configurable language model for assisted maintenance-report intake
- GitHub for source control and team collaboration
- Innoslate for systems modeling

## Toolchain Rationale

The selected technologies support rapid prototype development and provide a straightforward architecture for demonstrating the complete maintenance workflow from issue reporting through repair confirmation. The technology stack also allows the language-model component to remain configurable while the rest of the application architecture remains stable.

## Model Hosting Decision

DormFix will initially use a locally hosted language model through LM Studio. The selected initial model is Llama 3.1 8B Instruct.

## Model Hosting Rationale

Local model hosting avoids dependence on an external hosted API during the initial prototype stage and reduces concerns about sending maintenance-request data outside the local environment. It also allows the team to develop and test the AI-assisted intake interface without API usage costs or external-service availability dependencies.

The language model is an assistive component only. Its output remains editable by users, and DormFix provides a standard form-based reporting fallback if the model is unavailable.

## What Would Change This Decision

The team may reconsider local hosting if later testing shows that the selected model cannot satisfy required response quality, latency, hardware, or deployment constraints. A hosted model may then be evaluated as an alternative during a later trade study.

The team may revisit this toolchain if later testing identifies unacceptable performance, deployment limitations, integration difficulties, data-security concerns, or language-model capability limitations.

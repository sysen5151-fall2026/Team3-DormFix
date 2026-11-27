# DormFix Chapter 13

Use a new directory for the grading build. This source extends the course demonstration at GitHub revision 510a254f0f0f5857f774bf2e493ff082bc0be81e. The source tree and the PDF's attached ZIP contain the same grading entry point.

## Start

Use CPython 3.12. The grading path has no third-party Python packages. The Windows verification used CPython 3.12.14 and linked SQLite 3.53.1. The optional historical Streamlit and FastAPI paths have separate dependencies and are outside the grading setup.

1. Extract the source ZIP and change into the directory containing chapter13.py, or clone the enclosed Git bundle as described in START_HERE.txt. 
2. In terminal 1 run `python scripts/start_model.py`. On x64 Windows or Ubuntu this downloads llama.cpp b12801 and Qwen2.5-0.5B-Instruct GGUF Q4_K_M, verifies both SHA-256 hashes, then starts a CPU server at 127.0.0.1:8081. Leave it running. The weights and engine are cached outside the source. First use requires internet access. For Apple Silicon or an existing local model server, load a compatible instruct GGUF and start its OpenAI-compatible chat endpoint. Supply its real served name and URL with --model and --model-url.
3. In terminal 2 run `python chapter13.py --db data/ch13-demo.sqlite` and open http://127.0.0.1:8502/. The first launch seeds seven synthetic accounts and zero tickets. The same path reopens existing tickets on restart. For a fresh rehearsal, choose another new database filename.
4. As Alex Resident enter "The kitchen sink drips", building "Test Hall", room "101". Select **Prepare draft** with model assistance enabled. The source line must read **Language model** for the live demonstration. **Manual fallback** records an unavailable or malformed response. Review the proposed category, enter "After 4 PM", choose plumbing and select **Confirm and submit**. Record the returned ID and Submitted status.
5. Select Morgan Manager, locate that ID and assign Taylor Technician with Normal priority. As Taylor enter a progress note, then complete the job. As Alex confirm resolution, then reopen with a reason. Show the same ID and retained history. Administration sees aggregates. IT Support sees diagnostics and checkpoint controls.
6. For the failure demonstration run `python verify_ch13.py`. It uses its own temporary database and a deliberately wrong HTTP model fixture. To require the actual running weights, use `python verify_ch13.py --live`. Failure to obtain a model result fails this check. The ordinary web UI remains usable with manual intake.

## Checks and records

- `python -m unittest discover -s tests -v` runs the service, access, history, summary and recovery checks.
- `node --test tests/test_resident_ui.cjs` executes the shipped browser script with DOM/transport test controls. Node 24.21.0 was used only for this test.
- `python verify_inprocess.py` executes the fault campaign when sockets are unavailable. It uses actual REST handlers, the deployed model adapter and SQLite with an in-memory transport and synthetic model. Network timing and trained-weight inference are outside this mode.
- The 7-day repeat window is a demonstration setting. Set DORMFIX_REPEAT_DAYS to 1–365 before launch to change it. Repeat counting uses distinct reports in the same building/room/category, inclusive of the boundary. Deployment T requires owner agreement.
- The local model endpoint receives the report text and any entered category/access text. Separate contact, building and room fields are excluded from the model request. Use synthetic records. There is no SSO, real dispatch or institutional data feed. Photos and grouped trend analysis are outside this build.
- Model and trace evidence: docs/ch13/, contracts/ch13.md, docs/adr/0003-grading-build.md, docs/baselines/ and the original docs/prompt-log.md. Machine-readable evidence records identify the exact test mode.

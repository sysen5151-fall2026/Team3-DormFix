# Desktop installer sources

The repository root contains shared source and both platforms' launchers.
The mac/ and windows/ folders preserve the original 2026-10-26 installers and guides.
These installer templates require a sibling DormFix/ payload; do not run them here.

To assemble a package, copy the relevant platform template folder to a staging
folder outside this repository. Create DormFix/ inside that staging folder and
copy the repository application files, module folders, tests, docs and scripts
into it. Exclude .git/, packaging/, .venv/, __pycache__/, .env and runtime databases.
Retain .env.example. ZIP the resulting staging folder for a future GitHub Release.

To run directly from this repository, use python webapp.py or the platform's
Start DormFix launcher. The original ZIP archives were not committed.

For a GitHub source download on macOS, run chmod +x *.command *.sh in the project
folder before opening a launcher, or start it with python3 webapp.py. Web uploads
do not preserve executable file modes. Apply chmod +x to the installer .command
files when assembling a macOS package too.

"""Launch the integrated classroom UI, JSON API and SQLite service."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8502)
    parser.add_argument("--db", help="SQLite path (created and seeded on first start)")
    parser.add_argument("--model-url", default=os.getenv("DORMFIX_LLM_URL", "http://127.0.0.1:8081/v1/chat/completions"))
    parser.add_argument("--model", default=os.getenv("DORMFIX_LLM_MODEL", "dormfix-qwen"))
    args = parser.parse_args()
    if args.db:
        os.environ["DORMFIX_DB_PATH"] = args.db
    os.environ["DORMFIX_LLM_URL"] = args.model_url
    os.environ["DORMFIX_LLM_MODEL"] = args.model
    from webapp import Handler, ThreadingHTTPServer
    print(f"DormFix: http://127.0.0.1:{args.port}", flush=True)
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()

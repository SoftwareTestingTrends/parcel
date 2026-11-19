"""Command line: `parcel ask "question"` for one message, `parcel chat` to talk."""

import argparse
import json
import sys

from .assistant import Parcel
from .config import BACKENDS, Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="parcel", description="Hollow Lane's support assistant")
    parser.add_argument("--backend", choices=BACKENDS, help="overrides PARCEL_BACKEND")
    parser.add_argument("--model", help="overrides PARCEL_MODEL")
    parser.add_argument("--temperature", type=float, help="ollama only")
    parser.add_argument("--seed", type=int, help="ollama only")
    parser.add_argument("--no-trace", action="store_true", help="don't save a trace")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="send one or more messages, print the replies")
    ask.add_argument("messages", nargs="+", help="each argument is one customer message")
    ask.add_argument("--json", action="store_true", help="print the whole transcript as JSON")
    sub.add_parser("chat", help="talk to Parcel in the terminal")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env(
        backend=args.backend, model=args.model, temperature=args.temperature, seed=args.seed
    )
    parcel = Parcel(settings)
    if args.command == "ask":
        for message in args.messages:
            reply = parcel.ask(message)
            if not args.json:
                print(f"Parcel: {reply}")
        if args.json:
            print(json.dumps(parcel.transcript.to_dict(), indent=2))
    else:
        print(f"Parcel ({settings.backend}, {settings.model}). Type 'quit' to stop.")
        while True:
            try:
                message = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if message.lower() in {"quit", "exit"}:
                break
            if message:
                print(f"Parcel: {parcel.ask(message)}")
    if not args.no_trace:
        path = parcel.save()
        print(f"(trace saved to {path})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

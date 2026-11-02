"""Local launch tools; transport branching is not LENS-kind navigation logic."""

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(prog="zoomconnect", description="ZOOMCONNECT local prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run the positional collection and HASH example")
    sub.add_parser("legacy-demo", help="Run the preserved v0.1 UID-graph example")
    sub.add_parser("mixed-demo", help="Run mixed collection separation and reconnection")
    serve = sub.add_parser("serve", help="Open the local, isolated interactive demo")
    serve.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "demo":
        from .positions_demo import run_position_demo

        print(json.dumps(run_position_demo(), ensure_ascii=False, indent=2))
    elif args.command == "mixed-demo":
        from .positions_demo import run_mixed_demo

        print(json.dumps(run_mixed_demo(), ensure_ascii=False, indent=2))
    elif args.command == "legacy-demo":
        from .demo import run_demo

        print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
    else:
        from .positions_server import serve_positions

        serve_positions(port=args.port)

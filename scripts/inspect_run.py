"""Print every prompt and reply of one run, with visible delimiters, for reading by eye.

Usage:
  uv run scripts/inspect_run.py LOG.jsonl              # lists run ids with status
  uv run scripts/inspect_run.py LOG.jsonl RUN_ID       # prints that run
"""

import argparse
from pathlib import Path

from mas_sim.logs import format_run, read_log, run_records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=Path)
    ap.add_argument("run_id", nargs="?")
    args = ap.parse_args()
    records = read_log(args.log)
    if args.run_id is None:
        for r in run_records(records):
            print(f"{r['run_id']}  {r['status']}  {r['error'] or ''}")
        return
    print(format_run(records, args.run_id))


if __name__ == "__main__":
    main()

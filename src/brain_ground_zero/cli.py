from __future__ import annotations

import argparse
from pathlib import Path

from brain_ground_zero import reporting, runner
from brain_ground_zero.config import load_run_config


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain-vs-RAG Ground-Zero benchmark")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a benchmark family")
    run_p.add_argument("--family", required=True, help="Path to family config YAML")
    run_p.add_argument("--baselines", required=True, help="Path to baseline set YAML")
    run_p.add_argument("--system", default="configs/systems/default.yaml", help="Path to system config YAML")
    run_p.add_argument("--run-id", default=None, help="Optional run id")

    rep_p = sub.add_parser("report", help="Generate report artifacts")
    rep_p.add_argument("--run-dir", required=True, help="Run directory")

    smoke_p = sub.add_parser("smoke", help="Run a small smoke test")
    smoke_p.add_argument("--run-id", default="smoke_relational_drift", help="Optional run id")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.command == "run":
        cfg = load_run_config(args.family, args.baselines, args.system)
        run_dir = runner.run_benchmark(cfg, run_id=args.run_id)
        print(f"Run complete: {run_dir}")
    elif args.command == "report":
        reporting.generate_report(Path(args.run_dir))
    elif args.command == "smoke":
        cfg = load_run_config(
            "configs/families/relational_drift.yaml",
            "configs/baselines/all.yaml",
            "configs/systems/default.yaml",
        )
        run_dir = runner.run_benchmark(cfg, run_id=args.run_id, smoke=True)
        reporting.generate_report(run_dir)
        print(f"Smoke run complete: {run_dir}")


if __name__ == "__main__":
    main()


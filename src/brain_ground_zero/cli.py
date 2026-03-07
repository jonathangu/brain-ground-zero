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

    ms_p = sub.add_parser("multiseed", help="Run across multiple seeds and aggregate")
    ms_p.add_argument("--family", required=True, help="Path to family config YAML")
    ms_p.add_argument("--baselines", required=True, help="Path to baseline set YAML")
    ms_p.add_argument("--system", default="configs/systems/default.yaml", help="Path to system config YAML")
    ms_p.add_argument("--seeds", required=True, help="Comma-separated seed list, e.g. 1,2,3,4,5")
    ms_p.add_argument("--run-id", default=None, help="Optional run id")

    rep_p = sub.add_parser("report", help="Generate report artifacts")
    rep_p.add_argument("--run-dir", required=True, help="Run directory")

    smoke_p = sub.add_parser("smoke", help="Run a small smoke test")
    smoke_p.add_argument(
        "--family",
        default=None,
        help="Optional family config path (default: run all smoke families)",
    )
    smoke_p.add_argument("--run-id", default="smoke", help="Optional run id base")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.command == "run":
        cfg = load_run_config(args.family, args.baselines, args.system)
        run_dir = runner.run_benchmark(cfg, run_id=args.run_id)
        reporting.generate_report(run_dir)
        print(f"Run complete: {run_dir}")
    elif args.command == "multiseed":
        cfg = load_run_config(args.family, args.baselines, args.system)
        seeds = [int(s.strip()) for s in args.seeds.split(",")]
        run_dir = runner.run_multi_seed(cfg, seeds=seeds, run_id=args.run_id)
        reporting.generate_report(run_dir)
        print(f"Multi-seed run complete: {run_dir}")
    elif args.command == "report":
        reporting.generate_report(Path(args.run_dir))
    elif args.command == "smoke":
        if args.family:
            family_paths = [args.family]
        else:
            family_paths = [
                "configs/families/relational_drift.yaml",
                "configs/families/recurring_workflows.yaml",
                "configs/families/sparse_feedback.yaml",
            ]
        for family_path in family_paths:
            cfg = load_run_config(
                family_path,
                "configs/baselines/all.yaml",
                "configs/systems/default.yaml",
            )
            family_name = cfg.family.get("name", Path(family_path).stem)
            run_id = args.run_id if args.family else f"{args.run_id}_{family_name}"
            run_dir = runner.run_benchmark(cfg, run_id=run_id, smoke=True)
            reporting.generate_report(run_dir)
            print(f"Smoke run complete: {run_dir}")


if __name__ == "__main__":
    main()

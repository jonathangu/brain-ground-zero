from __future__ import annotations

import argparse
import time
from pathlib import Path

from brain_ground_zero import recorded_h2h, reporting, runner
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

    gf_p = sub.add_parser("generate_fixture", help="Generate a fixed session fixture from a family config")
    gf_p.add_argument("--family", required=True, help="Path to family config YAML")
    gf_p.add_argument("--seed", type=int, default=42, help="Generator seed (default: 42)")
    gf_p.add_argument("--output", required=True, help="Output fixture YAML path")

    rh_p = sub.add_parser("recorded_h2h", help="Run baselines against a fixed fixture with trace logging")
    rh_p.add_argument("--fixture", required=True, help="Path to fixture YAML")
    rh_p.add_argument("--baselines", required=True, help="Path to baseline set YAML")
    rh_p.add_argument("--output", required=True, help="Output bundle directory")
    rh_p.add_argument("--status", default="draft", help="Bundle status metadata value (default: draft)")

    rhm_p = sub.add_parser(
        "recorded_h2h_multiseed",
        help="Run recorded head-to-head across multiple seeds and aggregate proof artifacts",
    )
    rhm_p.add_argument("--family", required=True, help="Path to family config YAML")
    rhm_p.add_argument("--baselines", required=True, help="Path to baseline set YAML")
    rhm_p.add_argument("--seeds", required=True, help="Comma-separated seed list, e.g. 11,22,33")
    rhm_p.add_argument("--run-id", default=None, help="Optional run id (directory under runs/)")
    rhm_p.add_argument("--output-dir", default="runs", help="Output root directory (default: runs)")
    rhm_p.add_argument("--status", default="draft", help="Per-seed bundle status metadata value")

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
    elif args.command == "generate_fixture":
        recorded_h2h.generate_fixture(args.family, args.seed, args.output)
    elif args.command == "recorded_h2h":
        recorded_h2h.run_recorded_h2h(args.fixture, args.baselines, args.output, status=args.status)
    elif args.command == "recorded_h2h_multiseed":
        seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
        if args.run_id:
            run_dir = Path(args.output_dir) / args.run_id
        else:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            run_dir = Path(args.output_dir) / f"recorded_h2h_multiseed_{Path(args.family).stem}_{stamp}"
        recorded_h2h.run_recorded_h2h_multiseed(
            family_path=args.family,
            baselines_path=args.baselines,
            seeds=seeds,
            run_dir=run_dir,
            status=args.status,
        )
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

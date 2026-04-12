"""
Autonomous OODA loop — observe funnel state, orient, decide, act.

Replaces the old sequential orchestrator.py with a continuous loop that
evaluates the funnel on every iteration and dispatches only what's needed.

Usage:
  python3 scripts/autonomous_loop.py                  # run forever
  python3 scripts/autonomous_loop.py --dry-run        # print decisions, don't dispatch
  python3 scripts/autonomous_loop.py --run-once       # single iteration then exit
  python3 scripts/autonomous_loop.py --dry-run --run-once  # QA mode
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (  # noqa: E402
    LOOP_SLEEP_SECONDS,
    MIN_NEW_LEADS_THRESHOLD,
    _SCRIPTS_DIR as SCRIPTS_DIR,
)
from state_manager import count_by_status, init_db  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("autonomous_loop")

_running: dict[str, subprocess.Popen] = {}


def _is_running(name: str) -> bool:
    """Return True if *name* was dispatched and hasn't exited yet."""
    proc = _running.get(name)
    if proc is None:
        return False
    if proc.poll() is None:
        return True
    # Process finished — reap it
    del _running[name]
    return False


def dispatch(script: str, *, dry_run: bool = False) -> None:
    """Launch *script* non-blocking via Popen. Skip if already running."""
    if _is_running(script):
        log.info("SKIP %s — already running (pid %s)", script, _running[script].pid)
        return

    if dry_run:
        log.info("[DRY-RUN] Would dispatch: %s", script)
        return

    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        log.warning("SKIP %s — script file not found: %s", script, script_path)
        return

    log.info("DISPATCH %s", script)
    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _running[script] = proc


def _observe() -> dict[str, int]:
    """Query funnel state from SQLite."""
    try:
        counts = count_by_status()
    except Exception as exc:
        log.error("count_by_status() failed: %s", exc)
        counts = {}
    return counts


def _decide_and_act(counts: dict[str, int], iteration: int, *, dry_run: bool) -> None:
    """Full funnel decision tree — dispatch scripts based on counts."""

    # 1. Need more leads?
    if counts.get("new", 0) < MIN_NEW_LEADS_THRESHOLD:
        dispatch("strategy_agent.py", dry_run=dry_run)

    # 2. Enrich new leads
    if counts.get("new", 0) > 0:
        dispatch("enricher.py", dry_run=dry_run)

    # 3. Research enriched leads
    if counts.get("enriched", 0) > 0:
        dispatch("researcher.py", dry_run=dry_run)

    # 4. Generate proposals (researcher fills research col, doesn't change status)
    if counts.get("enriched", 0) > 0 or counts.get("needs_revision", 0) > 0:
        dispatch("generator.py", dry_run=dry_run)

    # 5. Blast draft-ready proposals (bypass reviewer per spec)
    if counts.get("draft_ready", 0) > 0:
        dispatch("blaster.py", dry_run=dry_run)

    # 6. Close replied leads
    if counts.get("replied", 0) > 0:
        dispatch("closer_agent.py", dry_run=dry_run)

    # 7. Periodic maintenance — every 5th iteration
    if iteration % 5 == 0:
        dispatch("sheets_sync.py", dry_run=dry_run)
        dispatch("followup.py", dry_run=dry_run)


def run_loop(*, dry_run: bool = False, run_once: bool = False) -> None:
    """Main OODA loop."""
    init_db()
    iteration = 0
    log.info(
        "Autonomous loop starting (dry_run=%s, run_once=%s, sleep=%ss, threshold=%s)",
        dry_run,
        run_once,
        LOOP_SLEEP_SECONDS,
        MIN_NEW_LEADS_THRESHOLD,
    )

    while True:
        iteration += 1
        try:
            # ── OBSERVE ──
            counts = _observe()
            total = sum(counts.values())
            log.info(
                "=== Iteration %d | %d total leads | Funnel: %s ===",
                iteration,
                total,
                counts or "(empty)",
            )

            # ── DECIDE + ACT ──
            _decide_and_act(counts, iteration, dry_run=dry_run)

        except Exception:
            log.exception("Iteration %d failed — continuing", iteration)

        if run_once:
            log.info("--run-once set. Exiting after single iteration.")
            break

        log.info("Sleeping %ds before next iteration...", LOOP_SLEEP_SECONDS)
        time.sleep(LOOP_SLEEP_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous OODA outreach loop")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print dispatch decisions without running scripts",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run one iteration then exit",
    )
    args = parser.parse_args()
    run_loop(dry_run=args.dry_run, run_once=args.run_once)


if __name__ == "__main__":
    main()

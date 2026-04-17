import subprocess
from datetime import datetime
from pathlib import Path

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


class OrchestratorService:

    def __init__(self, config: Settings):
        self.config = config
        self.scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"

    def run_full_pipeline(self, query: str, dry_run: bool = False) -> dict:
        industry, _, location_part = query.partition(" in ")
        location = location_part.strip() or "Jakarta, Indonesia"
        industry = industry.strip() or query

        logger.info(f"Starting {'DRY RUN' if dry_run else 'FULL'} pipeline")
        logger.info(f"Industry: {industry}, Location: {location}")

        results = {}

        results["vibe_scraper"] = self._run_step("vibe_scraper.py", "Discovering decision-maker leads via Vibe Prospecting", [industry, location, "20"])
        results["scraper"] = self._run_step("scraper.py", "Scraping additional leads via Google Places", [query])
        results["enricher"] = self._run_step("enricher.py", "Enriching contact info")
        results["researcher"] = self._run_step("researcher.py", "Researching prospect pain points")
        results["generator"] = self._run_step("generator.py", "Generating personalized proposals")
        results["reviewer"] = self._run_step("reviewer.py", "Reviewing proposal quality")
        results["generator_retry"] = self._run_step("generator.py", "Re-generating weak proposals")

        if not dry_run:
            results["blaster"] = self._run_step("blaster.py", "Sending proposals via email + WhatsApp")

        results["reply_tracker"] = self._run_step("reply_tracker.py", "Checking for replies (Gmail + WAHA)")

        if not dry_run:
            results["converter"] = self._run_step("converter.py", "Converting replies → meeting invites + PaperClip")

        results["followup"] = self._run_step("followup.py", "Sending follow-ups to non-responders")
        results["sheets_sync"] = self._run_step("sheets_sync.py", "Syncing funnel status to Google Sheet")
        results["brain_sync"] = self._brain_sync()

        logger.info("Pipeline complete")
        return results

    def run_followup_only(self) -> dict:
        logger.info("Starting follow-up cycle")
        results = {}
        results["reply_tracker"] = self._run_step("reply_tracker.py", "Checking for replies (Gmail + WAHA)")
        results["converter"] = self._run_step("converter.py", "Converting replies → meeting invites")
        results["followup"] = self._run_step("followup.py", "Sending follow-ups to non-responders")
        results["sheets_sync"] = self._run_step("sheets_sync.py", "Syncing funnel status to Google Sheet")
        results["brain_sync"] = self._brain_sync()
        logger.info("Follow-up cycle complete")
        return results

    def run_enrich_only(self) -> dict:
        logger.info("Starting enrichment cycle")
        results = {}
        results["enricher"] = self._run_step("enricher.py", "Enriching contact info")
        results["researcher"] = self._run_step("researcher.py", "Researching prospect pain points")
        results["sheets_sync"] = self._run_step("sheets_sync.py", "Syncing funnel status to Google Sheet")
        logger.info("Enrichment complete")
        return results

    def run_sync_only(self) -> dict:
        logger.info("Starting sync cycle")
        results = {}
        results["sheets_sync"] = self._run_step("sheets_sync.py", "Syncing funnel status to Google Sheet")
        results["brain_sync"] = self._brain_sync()
        logger.info("Sync complete")
        return results

    def _run_step(self, script: str, label: str, args: list = None) -> bool:
        if args is None:
            args = []
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] {label}")
        result = subprocess.run(
            ["python3", str(self.scripts_dir / script)] + args,
            capture_output=False,
        )
        if result.returncode != 0:
            logger.warning(f"{script} exited with code {result.returncode}. Continuing pipeline...")
        return result.returncode == 0

    def _brain_sync(self) -> bool:
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Syncing outcomes to hub brain")
        try:
            from leads import load_leads
            import brain_client as brain

            if not brain.is_online():
                logger.info("Hub brain offline — skipping brain sync")
                return False

            df = load_leads()
            if df is not None:
                brain.learn_batch_outcomes(df)
                stats = brain.stats()
                if stats:
                    total = stats.get("total", stats.get("file_based_memories", "?"))
                    logger.info(f"[brain] Total memories in hub: {total}")
            return True
        except Exception as e:
            logger.error(f"Brain sync error: {e}")
            return False

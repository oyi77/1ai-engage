# 1ai-engage

Cold Calling & Lead Automation System for BerkahKarya.

## Features
1. **Scraping**: Google Maps & Web via AgentCash (stableenrich).
2. **Enrichment**: Email & Phone number extraction via Minerva/Apollo.
3. **Drafting**: AI-generated proposals and WhatsApp messages.
4. **Blasting**: Automated sending via `wacli` and `himalaya`.

## Directory Structure
- `scripts/`: Python modules for each step.
- `data/`: Lead databases (`leads.csv`).
- `proposals/`: Generated proposals.
- `logs/`: Execution logs.

## Usage (via Telegram)
Tell Vilona:
- "Scrape leads for [Niche] in [City]"
- "Enrich our current leads"
- "Generate proposals for the leads"
- "Blast the leads"

Or run the orchestrator:
```bash
python3 scripts/orchestrator.py "Coffee Shop in Jakarta"
```

## Admin Control
Admin can monitor progress by asking Vilona for a "status update on 1ai-engage".
Vilona will report:
- Total leads found
- Leads enriched
- Proposals drafted
- Messages sent

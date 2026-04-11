# 1ai-engage Skill

Use this skill to manage cold calling and outbound engagement workflows.

## Workflow
1. **Targeting**: Define niche and location.
2. **Scraping**: Run `scripts/scraper.py "<query>"`.
3. **Enrichment**: Run `scripts/enricher.py` to fill emails/phones.
4. **Generation**: Run `scripts/generator.py` to create drafts in `proposals/`.
5. **Review**: (Optional) Admin reviews `proposals/`.
6. **Execution**: Run `scripts/blaster.py` to send.

## Tools Integrated
- `AgentCash (stableenrich)`: For Maps and Contact enrichment.
- `wacli`: For WhatsApp messaging.
- `himalaya`: For Email messaging.
- `gemini/oracle`: For proposal generation.

## Reporting
Always report progress to the Telegram admin after each step.
- Number of new leads.
- Enrichment success rate.
- Confirmation before blasting.

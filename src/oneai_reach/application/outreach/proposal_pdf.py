import html
import re
import time
from pathlib import Path

MAX_PROPOSAL_PDF_BYTES = 10 * 1024 * 1024


class ProposalPdfError(RuntimeError):
    pass


def proposal_pdf_filename(lead_name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", lead_name).strip("._-")
    return f"Proposal_{safe_name or 'Business'}.pdf"


def proposal_text_to_html(proposal: str, lead_name: str) -> str:
    escaped_lines = [html.escape(line.strip()) for line in proposal.splitlines()]
    paragraphs = "\n".join(
        "<p>&nbsp;</p>" if not line else f"<p>{line}</p>" for line in escaped_lines
    )
    escaped_name = html.escape(lead_name)
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 40px; color: #333; }}
        h1 {{ color: #1a1a2e; font-size: 22px; margin-bottom: 24px; }}
        p {{ margin: 12px 0; }}
        .proposal-meta {{ color: #666; font-size: 13px; margin-bottom: 28px; }}
    </style>
</head>
<body>
    <h1>Collaboration Proposal</h1>
    <div class="proposal-meta">Prepared for {escaped_name}</div>
    {paragraphs}
</body>
</html>"""


def generate_proposal_pdf(proposal: str, lead_name: str) -> bytes:
    """Generate PDF from proposal text. Returns empty bytes if generation fails."""
    try:
        from weasyprint import HTML as WeasyHTML
    except ImportError:
        return b""

    try:
        html_content = proposal_text_to_html(proposal, lead_name)
        start = time.perf_counter()
        pdf = WeasyHTML(string=html_content).write_pdf()
        duration = time.perf_counter() - start

        if not pdf or not pdf.startswith(b"%PDF"):
            return b""
        if len(pdf) > MAX_PROPOSAL_PDF_BYTES:
            return b""
        if duration > 10:
            return b""  # Too slow, skip PDF
        return pdf
    except Exception:
        # WeasyPrint fails on Python 3.13+ (collections.Callable issue etc)
        return b""


def persist_proposal_pdf(pdf_bytes: bytes, proposals_dir: str | Path, index: object, lead_name: str) -> Path:
    sent_dir = Path(proposals_dir).parent / "sent_pdfs"
    sent_dir.mkdir(parents=True, exist_ok=True)
    path = sent_dir / f"{index}_{proposal_pdf_filename(lead_name)}"
    path.write_bytes(pdf_bytes)
    return path

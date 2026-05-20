import html
import re
import time
from pathlib import Path

MAX_PROPOSAL_PDF_BYTES = 10 * 1024 * 1024


class ProposalPdfError(RuntimeError):
    pass


def proposal_text_to_html(proposal: str, lead_name: str) -> str:
    """Escape proposal text and lead name for safe HTML embedding."""
    return f"<p>{html.escape(proposal)}</p><p>Prepared for {html.escape(lead_name)}</p>"


def proposal_pdf_filename(lead_name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", lead_name).strip("._-")
    return f"Proposal_{safe_name or 'Business'}.pdf"


def _text_to_pdf_fpdf2(proposal: str, lead_name: str) -> bytes:
    """Generate PDF using fpdf2 (works on Python 3.13+)."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Collaboration Proposal", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Subtitle
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 10, f"Prepared for {lead_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # Body text
    pdf.set_font("Helvetica", "", 11)
    for line in proposal.splitlines():
        line = line.strip()
        if not line:
            pdf.ln(5)
        else:
            pdf.multi_cell(0, 7, line)
            pdf.ln(2)

    return pdf.output()


def generate_proposal_pdf(proposal: str, lead_name: str) -> bytes:
    """Generate PDF from proposal text. Returns empty bytes if generation fails."""
    try:
        pdf_bytes = _text_to_pdf_fpdf2(proposal, lead_name)
        if not pdf_bytes or len(pdf_bytes) < 100:
            return b""
        if len(pdf_bytes) > MAX_PROPOSAL_PDF_BYTES:
            return b""
        return pdf_bytes
    except Exception:
        return b""


def persist_proposal_pdf(pdf_bytes: bytes, proposals_dir: str | Path, index: object, lead_name: str) -> Path:
    sent_dir = Path(proposals_dir).parent / "sent_pdfs"
    sent_dir.mkdir(parents=True, exist_ok=True)
    path = sent_dir / f"{index}_{proposal_pdf_filename(lead_name)}"
    path.write_bytes(pdf_bytes)
    return path

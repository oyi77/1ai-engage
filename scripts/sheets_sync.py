"""
Sync leads.csv → Google Sheet (Investor tab).

Sheet columns (A–L):
  A: No
  B: Nama Kontak
  C: Perusahaan/Organisasi
  D: Jabatan/Peran
  E: Kategori Target
  F: Nomor Telepon / Email
  G: Tanggal Dihubungi
  H: Metode Kontak
  I: Respon Singkat
  J: Status Lanjutan
  K: Tanggal Follow-Up
  L: Catatan

Uses `gog sheets` CLI (free, no API cost).
Clears rows A3:L1000 first, then batch-appends all leads starting from row 3
(rows 1–2 are the header).
"""
import json
import os
import subprocess
import sys

import pandas as pd

from leads import load_leads
from utils import parse_display_name

SHEET_ID   = "10tRBCuRl_T6_nmdN1ycHaSRmsK-7jGKLtbJewKAUz_I"
SHEET_TAB  = "Investor"
DATA_RANGE = f"{SHEET_TAB}!A3:L1000"

GMAIL_ACCOUNT          = "moliangellina@gmail.com"
GMAIL_KEYRING_PASSWORD = "openclaw"

_GOG_ENV = {**os.environ, "GOG_KEYRING_PASSWORD": GMAIL_KEYRING_PASSWORD, "GOG_ACCOUNT": GMAIL_ACCOUNT}

STATUS_LABEL = {
    "new":            "Baru",
    "enriched":       "Data Dilengkapi",
    "draft_ready":    "Draft Siap",
    "needs_revision": "Perlu Revisi",
    "reviewed":       "Ditinjau",
    "contacted":      "Dihubungi",
    "followed_up":    "Follow-Up Terkirim",
    "replied":        "Membalas",
    "meeting_booked": "Meeting Dijadwalkan",
    "won":            "Berhasil",
    "lost":           "Gagal",
    "cold":           "Cold (Tidak Respon)",
    "unsubscribed":   "Unsubscribed",
}

RESPON_LABEL = {
    "replied":        "Ada balasan",
    "meeting_booked": "Minta meeting",
    "won":            "Deal!",
    "cold":           "Tidak ada respons",
    "followed_up":    "Belum ada respons",
    "contacted":      "-",
}


def _fmt_date(iso: str | None) -> str:
    if not iso or str(iso).lower() in ("nan", "none", ""):
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(str(iso))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(iso)[:10]


def _contact_method(row: pd.Series) -> str:
    has_email = str(row.get("email") or "").strip() not in ("", "nan", "none")
    has_phone = str(row.get("internationalPhoneNumber") or row.get("phone") or "").strip() not in ("", "nan", "none")
    if has_email and has_phone:
        return "Email + WhatsApp"
    if has_email:
        return "Email"
    if has_phone:
        return "WhatsApp"
    return "-"


def _contact_value(row: pd.Series) -> str:
    email = str(row.get("email") or "").strip()
    phone = str(row.get("internationalPhoneNumber") or row.get("phone") or "").strip()
    if email.lower() in ("nan", "none", ""):
        email = ""
    if phone.lower() in ("nan", "none", ""):
        phone = ""
    parts = [p for p in [email, phone] if p]
    return " / ".join(parts) if parts else "-"


def _catatan(row: pd.Series) -> str:
    issues = str(row.get("review_issues") or "").strip()
    score  = str(row.get("review_score") or "").strip()
    if issues.lower() in ("nan", "none", ""):
        issues = ""
    if score.lower() in ("nan", "none", ""):
        score = ""
    parts = []
    if score:
        parts.append(f"Score: {score}/10")
    if issues:
        # Truncate long review issues to keep cell readable
        short = issues[:120] + ("..." if len(issues) > 120 else "")
        parts.append(short)
    return " | ".join(parts) if parts else ""


def build_rows(df: pd.DataFrame) -> list[list[str]]:
    rows = []
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        name    = parse_display_name(row.get("displayName"))
        status  = str(row.get("status") or "new").strip()
        if status.lower() in ("nan", "none"):
            status = "new"

        rows.append([
            str(i),                                            # A: No
            name,                                              # B: Nama Kontak
            name,                                              # C: Perusahaan/Organisasi (same — no separate field)
            "",                                                # D: Jabatan/Peran
            str(row.get("primaryType") or row.get("type") or "Layanan").strip(),  # E: Kategori Target
            _contact_value(row),                               # F: Nomor Telepon / Email
            _fmt_date(row.get("contacted_at")),                # G: Tanggal Dihubungi
            _contact_method(row),                              # H: Metode Kontak
            RESPON_LABEL.get(status, "-"),                     # I: Respon Singkat
            STATUS_LABEL.get(status, status.title()),          # J: Status Lanjutan
            _fmt_date(row.get("followup_at")),                 # K: Tanggal Follow-Up
            _catatan(row),                                     # L: Catatan
        ])
    return rows


def _gog(args: list[str]) -> bool:
    result = subprocess.run(
        ["gog"] + args,
        capture_output=True, text=True, env=_GOG_ENV
    )
    if result.returncode != 0:
        print(f"  gog error: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def sync() -> None:
    df = load_leads()
    if df is None:
        return

    rows = build_rows(df)
    if not rows:
        print("No leads to sync.")
        return

    print(f"Syncing {len(rows)} leads to Google Sheet...")

    # Step 1: Clear existing data rows (keep header in rows 1–2)
    print("  Clearing old data (A3:L1000)...")
    cleared = _gog(["sheets", "clear", SHEET_ID, DATA_RANGE, "-j"])
    if not cleared:
        print("  Warning: clear failed — will still attempt append.", file=sys.stderr)

    # Step 2: Batch-append all rows
    values_json = json.dumps(rows)
    append_range = f"{SHEET_TAB}!A3:L3"  # gog appends starting from first empty row after this
    print(f"  Appending {len(rows)} rows...")
    ok = _gog(["sheets", "append", SHEET_ID, append_range, "--values-json", values_json, "-j"])

    if ok:
        print(f"✅ Sheet synced: {len(rows)} leads written.")
        print(f"   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    else:
        print("❌ Sheet sync failed. Check gog auth.", file=sys.stderr)


if __name__ == "__main__":
    sync()

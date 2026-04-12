import os
import sys
from pathlib import Path

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
scripts_dir = os.path.join(root_dir, "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import streamlit as st
import pandas as pd

from config import PROPOSALS_DIR
from leads import load_leads, save_leads


def parse_draft(content: str) -> tuple[str, str]:
    """
    Format is expected to be:
    ---PROPOSAL---
    <email content>
    ---WHATSAPP---
    <wa content>
    """
    parts = content.split("---WHATSAPP---")

    email_part = parts[0].replace("---PROPOSAL---", "").strip()

    wa_part = ""
    if len(parts) > 1:
        wa_part = parts[1].strip()

    return email_part, wa_part


def reconstruct_draft(email_content: str, wa_content: str) -> str:
    return f"---PROPOSAL---\n{email_content}\n---WHATSAPP---\n{wa_content}\n"


def render_editor():
    drafts_dir = Path(PROPOSALS_DIR)

    if not drafts_dir.exists():
        st.warning(f"Drafts directory '{drafts_dir}' not found.")
        return

    def sort_key(p):
        stem = p.stem
        idx_str = stem.split("_")[0]
        return int(idx_str) if idx_str.isdigit() else -1

    draft_files = sorted(drafts_dir.glob("*.txt"), key=sort_key)

    if not draft_files:
        st.info("No drafts found in the proposals directory.")
        return

    file_options = {f.name: f for f in draft_files}

    selected_filename = st.selectbox(
        "Select a draft to edit",
        options=list(file_options.keys()),
        format_func=lambda name: name.replace(".txt", "").replace("_", " "),
    )

    if not selected_filename:
        return

    selected_file = file_options[selected_filename]
    index_str = selected_filename.split("_")[0]

    try:
        content = selected_file.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return

    email_part, wa_part = parse_draft(content)

    df = load_leads()
    review_score = None

    if df is not None and index_str.isdigit():
        idx = int(index_str)
        if 0 <= idx < len(df):
            score = df.loc[idx, "review_score"]
            if pd.notna(score):
                review_score = str(score)

    if review_score:
        st.info(f"**Current Review Score:** {review_score}/10")

    with st.form("draft_editor_form"):
        st.markdown("### 📧 Email Content")
        new_email = st.text_area(
            "Email", value=email_part, height=300, label_visibility="collapsed"
        )

        st.markdown("### 💬 WhatsApp Message")
        new_wa = st.text_area(
            "WhatsApp", value=wa_part, height=150, label_visibility="collapsed"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            save_clicked = st.form_submit_button("💾 Save Draft")
        with col2:
            approve_clicked = st.form_submit_button("✅ Approve")

    if save_clicked:
        new_content = reconstruct_draft(new_email, new_wa)
        try:
            selected_file.write_text(new_content, encoding="utf-8")
            st.success("Draft saved successfully!")
        except Exception as e:
            st.error(f"Failed to save draft: {e}")

    if approve_clicked:
        if df is not None and index_str.isdigit():
            idx = int(index_str)
            if 0 <= idx < len(df):
                df.loc[idx, "status"] = "reviewed"
                try:
                    save_leads(df)
                    st.success(
                        f"Lead '{selected_filename}' approved! Status updated to 'reviewed'."
                    )
                except Exception as e:
                    st.error(f"Failed to update lead status: {e}")
            else:
                st.error(f"Lead index {idx} out of bounds in leads.csv.")
        else:
            st.error("Could not determine lead index or leads database not loaded.")

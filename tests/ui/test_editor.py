import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from ui.components.editor import parse_draft, reconstruct_draft, render_editor

def test_parse_draft_success():
    sample_draft = (
        "---PROPOSAL---\n"
        "Subject: Hello World\n\n"
        "This is the email.\n"
        "---WHATSAPP---\n"
        "Halo, ini WA.\n"
    )
    email_part, wa_part = parse_draft(sample_draft)
    
    assert email_part == "Subject: Hello World\n\nThis is the email."
    assert wa_part == "Halo, ini WA."

def test_parse_draft_missing_wa():
    sample_draft = (
        "---PROPOSAL---\n"
        "Subject: Hello World\n\n"
        "This is the email.\n"
    )
    email_part, wa_part = parse_draft(sample_draft)
    
    assert email_part == "Subject: Hello World\n\nThis is the email."
    assert wa_part == ""

def test_reconstruct_draft():
    email_part = "Subject: Hello\n\nEmail body"
    wa_part = "WhatsApp body"
    
    reconstructed = reconstruct_draft(email_part, wa_part)
    expected = (
        "---PROPOSAL---\n"
        "Subject: Hello\n\nEmail body\n"
        "---WHATSAPP---\n"
        "WhatsApp body\n"
    )
    
    assert reconstructed == expected

@patch("ui.components.editor.st")
@patch("ui.components.editor.load_leads")
@patch("ui.components.editor.save_leads")
@patch("ui.components.editor.Path")
def test_render_editor_approve_flow(mock_path, mock_save_leads, mock_load_leads, mock_st):
    # Given a mocked leads database and a mocked draft file
    mock_df = pd.DataFrame({
        "status": ["new", "draft_ready", "draft_ready"],
        "review_score": [None, 7, None]
    })
    mock_load_leads.return_value = mock_df
    
    mock_dir = MagicMock()
    mock_dir.exists.return_value = True
    
    mock_file = MagicMock()
    mock_file.name = "1_Test_Lead.txt"
    mock_file.stem = "1_Test_Lead"
    mock_file.read_text.return_value = "---PROPOSAL---\nEmail\n---WHATSAPP---\nWA\n"
    
    mock_dir.glob.return_value = [mock_file]
    mock_path.return_value = mock_dir
    
    mock_st.selectbox.return_value = "1_Test_Lead.txt"
    mock_st.form_submit_button.side_effect = [False, True]
    mock_col1, mock_col2 = MagicMock(), MagicMock()
    mock_st.columns.return_value = [mock_col1, mock_col2]
    
    # When the user clicks the approve button
    render_editor()
    
    # Then the lead status should be updated to 'reviewed'
    mock_save_leads.assert_called_once()
    
    args, kwargs = mock_save_leads.call_args
    updated_df = args[0]
    assert updated_df.loc[1, "status"] == "reviewed"
    assert updated_df.loc[0, "status"] == "new"
    
    mock_st.success.assert_called_with("Lead '1_Test_Lead.txt' approved! Status updated to 'reviewed'.")

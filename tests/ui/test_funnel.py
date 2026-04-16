from unittest.mock import patch, MagicMock
import pandas as pd
from ui.components.funnel import render_funnel


def test_render_funnel_empty_df():
    df = pd.DataFrame()
    with patch("ui.components.funnel.st") as mock_st:
        render_funnel(df=df)
        mock_st.info.assert_called_once_with("No leads found.")


@patch("ui.components.funnel.st")
def test_render_funnel_with_data(mock_st):
    df = pd.DataFrame({"status": ["new", "new", "enriched", "contacted", "won"]})

    mock_cols = [MagicMock() for _ in range(8)]
    mock_st.columns.return_value = mock_cols

    render_funnel(df=df)

    # Header was removed - page title is now handled by app.py
    mock_st.columns.assert_called_once_with(8)

    mock_cols[0].metric.assert_called_once_with(label="New", value=2)
    mock_cols[1].metric.assert_called_once_with(label="Enriched", value=1)
    mock_cols[4].metric.assert_called_once_with(label="Contacted", value=1)
    mock_cols[7].metric.assert_called_once_with(label="Won", value=1)

    mock_st.bar_chart.assert_called_once()
    chart_df = mock_st.bar_chart.call_args[0][0]
    assert len(chart_df) == 4
    assert chart_df.loc["new", "Count"] == 2


@patch("ui.components.funnel.os.path.exists", return_value=False)
@patch("ui.components.funnel.st")
def test_render_funnel_file_not_found(mock_st, mock_exists):
    render_funnel(df=None)
    mock_st.info.assert_called_once_with("No leads found.")

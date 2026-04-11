import json


def parse_display_name(raw) -> str:
    """Extract a business name from a raw displayName value (plain string or stringified dict)."""
    if isinstance(raw, str) and raw.startswith('{'):
        try:
            return json.loads(raw.replace("'", '"')).get('text', 'Business')
        except Exception:
            return 'Business'
    if raw and str(raw).lower() != 'nan':
        return str(raw)
    return 'Business'


def safe_filename(name: str) -> str:
    """Convert a name to a filesystem-safe string."""
    return "".join(c if c.isalnum() else "_" for c in str(name))


def draft_path(index: int, name: str) -> str:
    """Return the canonical path for a proposal draft file."""
    return f"1ai-engage/proposals/drafts/{index}_{safe_filename(name)}.txt"

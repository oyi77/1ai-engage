import sys
from oneai_reach.infrastructure.legacy._path import _ensure_scripts_path
_ensure_scripts_path()
from brain_client import *  # noqa: F401,F403

# Fallback definitions for compatibility with newer API logic using older scripts
WING_1AI = getattr(sys.modules.get('brain_client'), 'WING_1AI', "1ai-reach")
ROOM_OUTREACH = getattr(sys.modules.get('brain_client'), 'ROOM_OUTREACH', "outreach")
ROOM_PIPELINE = getattr(sys.modules.get('brain_client'), 'ROOM_PIPELINE', "pipeline")
ROOM_STRATEGY = getattr(sys.modules.get('brain_client'), 'ROOM_STRATEGY', "strategy")
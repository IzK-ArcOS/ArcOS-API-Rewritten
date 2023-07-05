from fastapi import APIRouter

from ..._shared import configuration as cfg, API_REVISION


router = APIRouter()


@router.get('/connect')
def connect():
    return {
        'platform': f"ArcOS @ {cfg['name']}",
        'port': cfg['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': API_REVISION
    }

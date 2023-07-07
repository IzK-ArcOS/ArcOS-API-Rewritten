from fastapi import APIRouter

from ..._shared import configuration as cfg, API_REVISION


router = APIRouter()


@router.get('/connect')
def connect():
    return {
        'platform': f"ArcOS @ {cfg['info']['name']}",
        'port': cfg['info']['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': API_REVISION
    }

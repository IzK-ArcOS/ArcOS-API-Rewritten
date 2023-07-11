from fastapi import APIRouter

from .. import EndpointTags
from ..._shared import configuration as cfg, API_REVISION


router = APIRouter(tags=[EndpointTags.server])


@router.get('/connect')
def connect():
    return {
        'platform': f"ArcOS @ {cfg['info']['name']}",
        'port': cfg['info']['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': API_REVISION
    }

from fastapi import APIRouter

from .. import EndpointTags
from ..._shared import configuration as cfg, API_REVISION


router = APIRouter(tags=[EndpointTags.meta])


@router.get('/connect', summary="Get ArcAPI instance information")
def connect():
    return {
        'platform': f"ArcOS @ {cfg['info']['name']}",
        'port': cfg['info']['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': API_REVISION,
        'protected': bool(cfg['security']['auth_code'])
    }

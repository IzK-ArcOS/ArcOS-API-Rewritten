from fastapi import APIRouter

from ..._shared import configuration as cfg, API_REVISION
from ._schemas import MetaInfo

router = APIRouter()


@router.get('/')
async def meta_info() -> MetaInfo:
    return MetaInfo(
        name=cfg['info']['name'],
        revision=API_REVISION,
        protected=bool(cfg['security']['auth_code']),
    )

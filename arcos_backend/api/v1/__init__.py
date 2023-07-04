import json
from typing import Annotated

from fastapi import Header, HTTPException, APIRouter
from starlette.requests import Request

from ._auth import parse_basic
from ... import _shared as shared


router = APIRouter()


@router.get(f'/auth')
def auth(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    username, password = parse_basic(authorization)

    token = shared.database.generate_token(username, password, shared.configuration['security']['token_lifetime'])

    return {'data': {'username': username, 'token': token}, 'valid': True, "error": {"title": "", "message": ""}}


@router.get(f'/logoff')
def logoff(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]

    shared.database.expire_token(token)


@router.get(f'/user/create')
def user_create(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    username, password = parse_basic(authorization)

    shared.database.create_user(username, password)
    user_id = shared.database.find_user(username)
    shared.filesystem.create_userspace(user_id)

    return {'error': {'valid': True}}


@router.get(f'/user/properties')
def user_properties(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    user_properties = shared.database.get_user_info(user_id)['account']['properties']

    return {**user_properties, 'valid': True, 'statusCode': 200}


@router.post(f'/user/properties/update')
async def user_properties_update(authorization: Annotated[str, Header()],  request: Request):
    properties = json.JSONDecoder().decode((await request.body()).decode('utf-8'))
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.set_user_properties(user_id, properties)


@router.get(f'/user/delete')
def user_delete(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.delete_user(user_id)


@router.get(f'/user/rename')
def user_rename(authorization: Annotated[str, Header()], newname: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.rename_user(user_id, newname)


@router.get(f'/user/changepswd')
def user_changepswd(authorization: Annotated[str, Header()], new: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.set_user_password(user_id, new)

    
@router.get(f'/connect')
def connect():
    return {
        'platform': f"ArcOS @ {shared.configuration['name']}",
        'port': shared.configuration['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': shared.API_REVISION
    }


@router.get(f'/users/get')
def users_get():
    user_ids = shared.database.get_user_ids()
    user_infos = [shared.database.get_user_info(user_id) for user_id in user_ids]
    user_infos = [{
        'username': info['username'],
        'acc': {
            'enabled': info['account']['enabled'],
            'admin': info['account']['admin'],
            'profilePicture': info['account']['profile_picture'],
            'properties': info['account']['properties']
        }
    } for info in user_infos]

    return {
        'data': user_infos,
        'valid': True
    }

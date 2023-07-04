import base64
import json
from typing import Annotated

from fastapi import Header, HTTPException, APIRouter, Response
from starlette.requests import Request

from ._auth import parse_basic
from ... import _shared as shared


router = APIRouter()


@router.get('/auth')
def auth(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    username, password = parse_basic(authorization)

    token = shared.database.generate_token(username, password, shared.configuration['security']['token_lifetime'])

    return {'data': {'username': username, 'token': token}, 'valid': True, "error": {"title": "", "message": ""}}


@router.get('/logoff')
def logoff(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]

    shared.database.expire_token(token)


@router.get('/user/create')
def user_create(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    username, password = parse_basic(authorization)

    shared.database.create_user(username, password)
    user_id = shared.database.find_user(username)
    shared.filesystem.create_userspace(user_id)

    return {'error': {'valid': True}}


@router.get('/user/properties')
def user_properties(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    user_properties = shared.database.get_user_info(user_id)['account']['properties']

    return {**user_properties, 'valid': True, 'statusCode': 200}


@router.post('/user/properties/update')
async def user_properties_update(authorization: Annotated[str, Header()],  request: Request):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    properties = json.JSONDecoder().decode((await request.body()).decode('utf-8'))

    shared.database.set_user_properties(user_id, properties)


@router.get('/user/delete')
def user_delete(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.delete_user(user_id)


@router.get('/user/rename')
def user_rename(authorization: Annotated[str, Header()], newname: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.rename_user(user_id, newname)


@router.get('/user/changepswd')
def user_changepswd(authorization: Annotated[str, Header()], new: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    shared.database.set_user_password(user_id, new)

    
@router.get('/connect')
def connect():
    return {
        'platform': f"ArcOS @ {shared.configuration['name']}",
        'port': shared.configuration['port'],
        'referrer': '/connect',
        'valid': True,
        'revision': shared.API_REVISION
    }


@router.get('/users/get')
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


@router.get('/fs/quota')
def fs_quota(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    used = shared.filesystem.get_size(user_id, '.')

    return {
        'data': {
            'username': shared.database.get_username(user_id),
            'max': (size := shared.filesystem.get_userspace_size()),
            'used': used,
            'free': size - used
        },
        'valid': True
    }


@router.get('/fs/dir/get')
def fs_dir_get(authorization: Annotated[str, Header()], path: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    path = base64.b64decode(path).decode('utf-8')

    files, directories = shared.filesystem.listdir(user_id, path)

    base_path = shared.filesystem.get_basepath(user_id)

    _name = lambda s: s[s.rfind('/') + 1:]  # NOQA E731
    _scope = lambda s: s[len(base_path)+1:]  # NOQA E731

    return {
        'valid': True,
        'data': {
            'name': _name(path),
            'scopedPath': path,
            'files': [{
                'filename': _name(file),
                'scopedPath': (scoped := _scope(file)),
                'size': shared.filesystem.get_size(user_id, scoped),
                'mime': shared.filesystem.get_mime(user_id, scoped)
            } for file in files],
            'directories': [{
                'name': _name(directory),
                'scopedPath': _scope(directory)
            } for directory in directories]
        }
    }


@router.get('/fs/dir/create')
def fs_dir_create(authorization: Annotated[str, Header()], path: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    path = base64.b64decode(path).decode('utf-8')

    shared.filesystem.mkdir(user_id, path)

    return {'valid': True}


@router.get('/fs/file/get')
def fs_file_get(response: Response, authorization: Annotated[str, Header()], path: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    path = base64.b64decode(path).decode('utf-8')

    response.headers['Content-Type'] = shared.filesystem.get_mime(user_id, path)
    response.body = shared.filesystem.read(user_id, path)
    response.status_code = 200

    return response


@router.post('/fs/file/write')
async def fs_file_write(authorization: Annotated[str, Header()], path: str, request: Request):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    path = base64.b64decode(path).decode('utf-8')
    file_data = await request.body()

    if shared.filesystem.get_size(user_id, '.') + len(file_data) > shared.filesystem.get_userspace_size():
        raise HTTPException(status_code=409, detail="there's not enough space free on your account")

    shared.filesystem.write(user_id, path, file_data)


@router.get('/fs/cp')
def fs_time_copy(authorization: Annotated[str, Header()], path: str, target: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    _b64 = lambda s: base64.b64decode(s).decode('utf-8')

    shared.filesystem.copy(user_id, _b64(path), _b64(target))


@router.get('/fs/rm')
def fs_rm(authorization: Annotated[str, Header()], path: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    path = base64.b64decode(path).decode('utf-8')

    shared.filesystem.delete(user_id, path)


@router.get('/fs/rename')
def fs_item_rename(authorization: Annotated[str, Header()], oldpath: str, newpath: str):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    _b64 = lambda s: base64.b64decode(s).decode('utf-8')

    shared.filesystem.move(user_id, _b64(oldpath), _b64(newpath))


@router.get('/fs/tree')
def fs_tree(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]
    user_id = shared.database.validate_token(token)
    if user_id is None: raise HTTPException(status_code=403)  # NOQA E701

    paths = shared.filesystem.get_tree(user_id, ".")

    return {
        'valid': True,
        'data': [{
            'scopedPath': path,
            'mime': shared.filesystem.get_mime(user_id, path),
            'filename': path[path.rfind('/') + 1:]
        } for path in paths]
    }

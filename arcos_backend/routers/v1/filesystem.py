import base64
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response
from starlette.requests import Request

from ._auth import bearer
from ..._shared import database as db, filesystem as fs


router = APIRouter()


@router.get('/quota')
def fs_quota(authorization: Annotated[str, Header()]):
    user_id = bearer(authorization)

    used = fs.get_size(user_id, '.')

    return {
        'data': {
            'username': db.get_username(user_id),
            'max': (size := fs.get_userspace_size()),
            'used': used,
            'free': size - used
        },
        'valid': True
    }


@router.get('/dir/get')
def fs_dir_get(authorization: Annotated[str, Header()], path: str):
    user_id = bearer(authorization)
    path = base64.b64decode(path).decode('utf-8')

    files, directories = fs.listdir(user_id, path)

    base_path = fs.get_basepath(user_id)

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
                'size': fs.get_size(user_id, scoped),
                'mime': fs.get_mime(user_id, scoped)
            } for file in files],
            'directories': [{
                'name': _name(directory),
                'scopedPath': _scope(directory)
            } for directory in directories]
        }
    }


@router.get('/dir/create')
def fs_dir_create(authorization: Annotated[str, Header()], path: str):
    user_id = bearer(authorization)
    path = base64.b64decode(path).decode('utf-8')

    fs.mkdir(user_id, path)

    return {'valid': True}


@router.get('/file/get')
def fs_file_get(response: Response, authorization: Annotated[str, Header()], path: str):
    user_id = bearer(authorization)
    path = base64.b64decode(path).decode('utf-8')

    response.headers['Content-Type'] = fs.get_mime(user_id, path)
    response.body = fs.read(user_id, path)
    response.status_code = 200

    return response


@router.post('/file/write')
async def fs_file_write(request: Request, authorization: Annotated[str, Header()], path: str):
    user_id = bearer(authorization)
    path = base64.b64decode(path).decode('utf-8')
    file_data = await request.body()

    if fs.get_size(user_id, '.') + len(file_data) > fs.get_userspace_size():
        raise HTTPException(status_code=409, detail="there's not enough space free on your account")

    fs.write(user_id, path, file_data)


@router.get('/cp')
def fs_time_copy(authorization: Annotated[str, Header()], path: str, target: str):
    user_id = bearer(authorization)

    _b64 = lambda s: base64.b64decode(s).decode('utf-8')

    fs.copy(user_id, _b64(path), _b64(target))


@router.get('/rm')
def fs_rm(authorization: Annotated[str, Header()], path: str):
    user_id = bearer(authorization)
    path = base64.b64decode(path).decode('utf-8')

    fs.delete(user_id, path)


@router.get('/rename')
def fs_item_rename(authorization: Annotated[str, Header()], oldpath: str, newpath: str):
    user_id = bearer(authorization)

    _b64 = lambda s: base64.b64decode(s).decode('utf-8')

    fs.move(user_id, _b64(oldpath), _b64(newpath))


@router.get('/tree')
def fs_tree(authorization: Annotated[str, Header()]):
    user_id = bearer(authorization)

    paths = fs.get_tree(user_id, ".")

    return {
        'valid': True,
        'data': [{
            'scopedPath': path,
            'mime': fs.get_mime(user_id, path),
            'filename': path[path.rfind('/') + 1:]
        } for path in paths]
    }

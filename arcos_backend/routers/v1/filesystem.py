import base64
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Depends
from starlette.requests import Request

from ._common import auth_bearer, get_path
from ..._shared import filesystem as fs
from ...davult import models


router = APIRouter()


@router.get('/quota')
def fs_quota(user: Annotated[models.User, Depends(auth_bearer)]):
    used = fs.get_size(user.id, '.')

    return {
        'data': {
            'username': user.username,
            'max': (size := fs.get_userspace_size()),
            'used': used,
            'free': size - used
        },
        'valid': True
    }


@router.get('/dir/get')
def fs_dir_get(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    try:
        files, directories = fs.listdir(user.id, path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    base_path = fs.get_basepath(user.id)

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
                'size': fs.get_size(user.id, scoped),
                'mime': fs.get_mime(user.id, scoped)
            } for file in files],
            'directories': [{
                'name': _name(directory),
                'scopedPath': _scope(directory)
            } for directory in directories]
        }
    }


@router.get('/dir/create')
def fs_dir_create(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    try:
        fs.mkdir(user.id, path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    return {'valid': True}


@router.get('/file/get')
def fs_file_get(response: Response, user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    try:
        response.headers['Content-Type'] = fs.get_mime(user.id, path)
        response.body = fs.read(user.id, path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    response.status_code = 200

    return response


@router.post('/file/write')
async def fs_file_write(request: Request, user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    file_data = await request.body()

    try:
        fs.write(user.id, path, file_data)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")
    except RuntimeError:
        raise HTTPException(status_code=409, detail="data is too large (not enough space)")


@router.get('/cp')
def fs_time_copy(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)], target: str):
    target = base64.b64decode(target).decode('utf-8')

    try:
        fs.write(user.id, target, fs.read(user.id, path))
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")
    except RuntimeError:
        raise HTTPException(status_code=409, detail="data is too large (not enough space)")


@router.get('/rm')
def fs_rm(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    try:
        fs.delete(user.id, path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")


@router.get('/rename')
def fs_item_rename(user: Annotated[models.User, Depends(auth_bearer)], oldpath: str, newpath: str):
    _b64 = lambda s: base64.b64decode(s).decode('utf-8')

    try:
        fs.move(user.id, _b64(oldpath), _b64(newpath))
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")


@router.get('/tree')
def fs_tree(user: Annotated[models.User, Depends(auth_bearer)]):
    try:
        paths = fs.get_tree(user.id, ".")
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    return {
        'valid': True,
        'data': [{
            'scopedPath': path,
            'mime': fs.get_mime(user.id, path),
            'filename': path[path.rfind('/') + 1:]
        } for path in paths]
    }

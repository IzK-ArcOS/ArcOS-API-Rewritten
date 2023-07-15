import base64
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Depends
from starlette.requests import Request

from ._common import auth_bearer, get_path
from .. import EndpointTags
from ..._shared import filesystem as fs
from ...davult import models
from ...filesystem import Userspace


router = APIRouter(tags=[EndpointTags.filesystem])


@router.get('/quota', summary="Get available space in user storage")
def fs_quota(user: Annotated[models.User, Depends(auth_bearer)]):
    userspace = Userspace(fs, user.id)

    used = userspace.get_size('.')

    return {
        'data': {
            'username': user.username,
            'max': (size := fs.get_userspace_size()),
            'used': used,
            'free': size - used
        },
        'valid': True
    }


@router.get('/dir/get', summary="List the directory")
def fs_dir_get(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    userspace = Userspace(fs, user.id)

    try:
        files, directories = userspace.listdir(path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    base_path = userspace.get_root()

    _name = lambda s: s[s.rfind(os.sep) + 1:]  # NOQA E731
    _scope = lambda s: s[len(base_path)+1:]  # NOQA E731

    return {
        'valid': True,
        'data': {
            'name': _name(path),
            'scopedPath': path,
            'files': [{
                'filename': _name(file),
                'scopedPath': (scoped := _scope(file)),
                'size': userspace.get_size(scoped),
                'mime': userspace.get_mime(scoped)
            } for file in files],
            'directories': [{
                'name': _name(directory),
                'scopedPath': _scope(directory)
            } for directory in directories]
        }
    }


@router.get('/dir/create', summary="Create the directory")
def fs_dir_create(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    userspace = Userspace(fs, user.id)

    try:
        userspace.mkdir(path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    return {'valid': True}


@router.get('/file/get', summary="Read the file")
def fs_file_get(response: Response, user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    userspace = Userspace(fs, user.id)

    try:
        response.headers['Content-Type'] = userspace.get_mime(path)
        response.body = userspace.read(path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    response.status_code = 200

    return response


@router.post('/file/write', summary="Write to the file")
async def fs_file_write(request: Request, user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    file_data = await request.body()

    userspace = Userspace(fs, user.id)

    try:
        userspace.write(path, file_data)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")
    except RuntimeError:
        raise HTTPException(status_code=409, detail="data is too large (not enough space)")


@router.get('/cp', summary="Copy the file or the directory")
def fs_time_copy(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)], target: str):
    target = base64.b64decode(target).decode('utf-8')

    userspace = Userspace(fs, user.id)

    try:
        userspace.write(target, userspace.read(path))
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")
    except RuntimeError:
        raise HTTPException(status_code=409, detail="data is too large (not enough space)")


@router.get('/rm', summary="Delete the file or the directory")
def fs_rm(user: Annotated[models.User, Depends(auth_bearer)], path: Annotated[str, Depends(get_path)]):
    userspace = Userspace(fs, user.id)

    try:
        userspace.remove(path)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")


@router.get('/rename', summary="Rename (move) the file or the directory")
def fs_item_rename(user: Annotated[models.User, Depends(auth_bearer)], oldpath: str, newpath: str):
    _b64 = lambda s: base64.b64decode(s).decode('utf-8')  # NOQA E731

    userspace = Userspace(fs, user.id)

    try:
        userspace.move(_b64(oldpath), _b64(newpath))
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")


@router.get('/tree', summary="Get the tree of the userspace")
def fs_tree(user: Annotated[models.User, Depends(auth_bearer)]):
    userspace = Userspace(fs, user.id)

    try:
        paths = userspace.get_tree(".")
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="path not found")

    return {
        'valid': True,
        'data': [{
            'scopedPath': path,
            'mime': userspace.get_mime(path),
            'filename': path[path.rfind(os.sep) + 1:]
        } for path in paths]
    }

import os
import base64
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Depends
from starlette.requests import Request

from ._common import auth_bearer, get_path
from .. import EndpointTags
from ..._shared import filesystem as fs, configuration as cfg
from ...davult import models
from ...filesystem.userspace import Userspace


router = APIRouter(tags=[EndpointTags.filesystem])


@router.get('/quota', summary="Get available space in user storage")
def fs_quota(user: Annotated[models.User, Depends(auth_bearer)]):
    userspace = Userspace(fs, user.id)

    size = fs.get_userspace_size()
    used = userspace.get_size('.')

    return {
        'data': {
            'username': user.username,
            'max': size,
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

    # base_path = userspace.get_root()

    _deep_adapt = lambda path: Path() / cfg['storage']['root'] / cfg['storage']['filesystem'] / _adapt(path)
    _adapt = lambda path: Path(str(user.id)) / path
    _norm = lambda path: Path(_deep_adapt(path)).resolve().relative_to(userspace._root.absolute())
    _scope = lambda path, level: (path := _norm(path)).relative_to(path.parents[-level])

    return {
        'valid': True,
        'data': {
            'name': Path(path).name,
            'scopedPath': str(_norm(path)),
            'files': [{
                'filename': file.name,
                'scopedPath': _scope(file, 3),
                # FIXME wtf
                'size': userspace._fs.get_size(_adapt(_scope(_adapt(file), 4))),
                'mime': userspace._fs.get_mime(_adapt(_scope(_adapt(file), 4)))
            } for file in files],
            'directories': [{
                'name': Path(directory).name,
                'scopedPath': _scope(directory, 3)
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
    except FileExistsError:
        raise HTTPException(status_code=409)

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
        # FIXME uhh... it doesnt work?
        userspace.copy(target, path)
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
            'scopedPath': os.path.normpath(path),
            'mime': userspace.get_mime(path),
            'filename': path[path.rfind(os.sep) + 1:]
        } for path in paths]
    }

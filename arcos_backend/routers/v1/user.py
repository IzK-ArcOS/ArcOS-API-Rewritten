import json
from typing import Annotated

from fastapi import APIRouter, Header
from starlette.requests import Request

from ._auth import basic, bearer
from ..._shared import database as db, filesystem as fs


router = APIRouter()


@router.get('/create')
def user_create(authorization: Annotated[str, Header()]):
    username, password = basic(authorization)

    db.create_user(username, password)
    user_id = db.find_user(username)
    fs.create_userspace(user_id)

    return {'error': {'valid': True}}


@router.get('/properties')
def user_properties(authorization: Annotated[str, Header()]):
    user_id = bearer(authorization)

    user_properties = db.get_user_info(user_id)['account']['properties']

    return {**user_properties, 'valid': True, 'statusCode': 200}


@router.post('/properties/update')
async def user_properties_update(authorization: Annotated[str, Header()],  request: Request):
    user_id = bearer(authorization)

    # plz tell izaak to set header `content-type` to `application/json` in the frontend, this is truly awful
    properties = json.JSONDecoder().decode((await request.body()).decode('utf-8'))

    db.set_user_properties(user_id, properties)


@router.get('/delete')
def user_delete(authorization: Annotated[str, Header()]):
    user_id = bearer(authorization)

    db.delete_user(user_id)


@router.get('/rename')
def user_rename(authorization: Annotated[str, Header()], newname: str):
    user_id = bearer(authorization)

    db.rename_user(user_id, newname)


@router.get('/changepswd')
def user_changepswd(authorization: Annotated[str, Header()], new: str):
    user_id = bearer(authorization)

    db.set_user_password(user_id, new)

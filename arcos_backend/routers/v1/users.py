from fastapi import APIRouter

from ..._shared import database as db


router = APIRouter()


@router.get('/get')
def users_get():
    user_ids = db.get_user_ids()
    user_infos = [db.get_user_info(user_id) for user_id in user_ids]
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

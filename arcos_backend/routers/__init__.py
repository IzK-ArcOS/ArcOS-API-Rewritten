from enum import StrEnum


class EndpointTags(StrEnum):
    filesystem = "filesystem"
    messages = "messages"
    users = "users"
    sessions = "sessions"
    server = "server"
    admin = "admin"


TAGS_DOCS = [
    {
        'name': EndpointTags.filesystem,
        'description': "Interaction with ArcFS"
    },
    {
        'name': EndpointTags.messages,
        'description': "Endpoints implementing basic messaging email-like protocol"
    },
    {
        'name': EndpointTags.users,
        'description': "User accounts management"
    },
    {
        'name': EndpointTags.sessions,
        'description': "Session (token) management"
    },
    {
        'name': EndpointTags.server,
        'description': "ArcAPI instance information"
    },
    {
        'name': EndpointTags.admin,
        'description': "Administration of user accounts"
    }
]

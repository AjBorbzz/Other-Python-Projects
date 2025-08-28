from fastapi import Depends

def get_current_user():
    # TODO: replace with JWT or OIDC
    return {"sub": "demo-user", "roles": ["analyst"]}
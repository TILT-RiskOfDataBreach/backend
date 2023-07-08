from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pycountry import countries

from ..database.authentication import Authentication
from .authentication import authenticate
from ..database.models.models import User, NewUser
from ..database.models.http_responses import *



# Definition - access_lvl
# 0 Default, can update data sharing network and risk estimates
# 1 Admin, has admin access



router = APIRouter(
    tags=["login"]
)

#<------------------------>
#        API-Login
#<------------------------>

@router.get("/is_username/{username}", responses=default_responses)
async def is_username(username: str, user: User = Depends(authenticate)):
    """
    Check if given username already exists.
    """
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    return JSONResponse(status_code=200, content=Authentication.is_username(username))

post_responses = {
    **default_responses,
    400: {"model": ModelMessage, "description": "Invalid country or user."},
}

@router.post("/signup", responses=post_responses)
async def signup(new_user: NewUser, user: User = Depends(authenticate)):
    """
    Register a new user in the system. Only accessible for access level >= 3 (authority).
    """
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization level!"})

    if countries.get(alpha_2=new_user.country) is None:
        return JSONResponse(status_code=400, content={"message": "Country does not exist!"})

    if not Authentication.signup(new_user.dict()):
        return JSONResponse(status_code=400, content={"message": "User already exists!"})

    return JSONResponse(status_code=200, content={"acknowledged": True})
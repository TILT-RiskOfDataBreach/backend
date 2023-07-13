from fastapi import APIRouter, HTTPException, Depends
from fastapi_utils.tasks import repeat_every
from fastapi.responses import JSONResponse

from ..database.models.http_responses import *
from ..routers.authentication import User, authenticate
from ..database.analysis import update


router = APIRouter(
    tags=["analysis"]
)


# <------------------------>
#       API-Analysis
# <------------------------>

@router.get("/update", responses=default_responses)
async def analysis(user: User = Depends(authenticate)):
    if user["access_lvl"] != 0 and user["access_lvl"] != 1:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    print("updating...")
    update()
    print("updated!")

    return JSONResponse(status_code=200, content={"acknowledged": True})

@router.on_event("startup")
@repeat_every( seconds= 60 * 60 * 24 )
async def __analysis():
    print("updating...")
    update()
    print("updated!")

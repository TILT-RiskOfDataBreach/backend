from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from .authentication import User, authenticate
from ..database.data import insert_tilt, insert_tilts, delete_tilt, delete_tilts
from ..database.models.http_responses import *


router = APIRouter(
    tags=["data"]
)


# <------------------------>
#         API-Data
# <------------------------>

@router.post("/tilt/insert", responses={**default_responses, 400: {"model": ModelMessage}})
async def insert_tilt(tilt: Request, user: User = Depends(authenticate)):
    """
    POSTs a new TILT document to the database.
    """
    if user["access_lvl"] != 0 and user["access_lvl"] != 1:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    if insert_tilt(tilt) is False:
        return JSONResponse(status_code=400, content={"message": "Error in system, TILT could not be added or updated."})

    return JSONResponse(status_code=200, content={"acknowledged": True})

@router.post("/tilts/insert", responses={**default_responses, 400: {"model": ModelMessage}})
async def insert_tilts(tilts: Request, user: User = Depends(authenticate)):
    """
    POSTs multiple new TILT documents to the database.
    """
    if user["access_lvl"] != 0 and user["access_lvl"] != 1:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    if insert_tilts(tilts) is False:
        return JSONResponse(status_code=400, content={"message": "Error in system, TILTs could not be added or updated."})

    return JSONResponse(status_code=200, content={"acknowledged": True})

@router.delete("/tilt/delete", responses={**default_responses, 400: {"model": ModelMessage}})
async def delete_tilt(tilt: Request, user: User = Depends(authenticate)):
    """
    DELETEs a TILT document from the database.
    """
    if user["access_lvl"] != 0 and user["access_lvl"] != 1:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    if delete_tilt(tilt) is False:
        return JSONResponse(status_code=400, content={"message": "Error in system, TILT could not be deleted."})

    return JSONResponse(status_code=200, content={"acknowledged": True})

@router.delete("/tilts/delete", responses={**default_responses, 400: {"model": ModelMessage}})
async def delete_tilts(tilts: Request, user: User = Depends(authenticate)):
    """
    DELETEs multiple TILT documents from the database.
    """
    if user["access_lvl"] != 0 and user["access_lvl"] != 1:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    if delete_tilts(tilts) is False:
        return JSONResponse(status_code=400, content={"message": "Error in system, TILTs could not be deleted."})

    return JSONResponse(status_code=200, content={"acknowledged": True})

from fastapi import APIRouter, HTTPException

from ..database.models.http_responses import *
from ..database.risk import get_risk


router = APIRouter(
    tags=["risk"]
)


# <------------------------>
#       API-Get_Risk
# <------------------------>

@router.get("/{domain}", responses={**default_responses, 400: {"model": ModelMessage}})
async def create(domain: str):
    """
    GETs risk score of specified domain
    """
    risk = get_risk(domain)
    if risk is None:
        raise HTTPException(status_code=400, detail="No risk estimate found.")
    return risk

from fastapi import APIRouter, Request
from services.seating import create_seating_service
from schemas.seating import CreateSeatingRequest

router: APIRouter = APIRouter()

@router.post("/seating/create")
def create_seating(request: Request, args:CreateSeatingRequest):
    """
    Create a new seating arrangement.
    """
    return create_seating_service(request, args)
    
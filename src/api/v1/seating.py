from fastapi import APIRouter, Request
from services.seating import create_seating as create_seating_service

router: APIRouter = APIRouter()

@router.post("/create")
def create_seating(request: Request):
    """
    Create a new seating arrangement.
    """
    create_seating_service(request)
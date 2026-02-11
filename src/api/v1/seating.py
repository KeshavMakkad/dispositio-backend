from fastapi import APIRouter, Request

router: APIRouter = APIRouter()

@router.post("/seating/create")
def create_seating(request: Request):
    """
    Create a new seating arrangement.
    """
    pass
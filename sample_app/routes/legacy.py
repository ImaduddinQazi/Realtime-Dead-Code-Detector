from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["legacy"])

@router.get("/old-payment")
def old_payment():
    return {"message": "legacy endpoint"}

@router.post("/legacy-signup")
def legacy_signup():
    return {"message": "legacy endpoint"}
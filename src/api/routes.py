from fastapi import APIRouter

router = APIRouter()


@router.get("")
def read_root() -> dict[str, str]:
    return {"message": "Microservice is running"}


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "pong"}

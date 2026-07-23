from fastapi import FastAPI, Depends

from app.dependency import x_cleint_checker
from app.routers.user import router as  user_router
from app.routers.event import router as event_router
from app.routers.booking import router as booking_router

app = FastAPI(dependencies=[Depends(x_cleint_checker)])

app.include_router(user_router)
app.include_router(event_router)
app.include_router(booking_router)


from fastapi import FastAPI

from app.routers.user import router as  user_router
from app.routers.event import router as event_router
from app.routers.booking import router as booking_router
from app.routers.auth import router as auth_router


app = FastAPI()

app.include_router(user_router)
app.include_router(event_router)
app.include_router(booking_router)
app.include_router(auth_router)




# main.py
from fastapi import FastAPI
from app.core.config import settings
from app.apis.v1.endpoints import user, email, event
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(event.router, prefix=f"{settings.API_V1_STR}/events", tags=["events"])
app.include_router(email.router, prefix=f"{settings.API_V1_STR}/emails", tags=["emails"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Event Management CRM API!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
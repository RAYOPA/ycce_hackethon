from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, personnel, wellness, support, interventions, notifications, analytics, admin, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(personnel.router, prefix=f"{settings.API_V1_STR}/personnel", tags=["personnel"])
app.include_router(wellness.router, prefix=f"{settings.API_V1_STR}/wellness", tags=["wellness"])
app.include_router(support.router, prefix=f"{settings.API_V1_STR}/support", tags=["support"])
app.include_router(interventions.router, prefix=f"{settings.API_V1_STR}/interventions", tags=["interventions"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "Welcome to ManRakshak API"}

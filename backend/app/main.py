import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.api.v1 import auth, personnel, wellness, support, interventions, notifications, analytics, admin, reports, privacy, ai as ai_router_module
from app.ai.exceptions import AIGatewayError, AIConfigurationError, AIUnavailableError

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Global Exception Handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

@app.exception_handler(AIGatewayError)
async def ai_gateway_exception_handler(request: Request, exc: AIGatewayError):
    """Map AI Gateway errors to safe HTTP responses — never leaks provider internals."""
    if isinstance(exc, AIConfigurationError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, AIUnavailableError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        code = status.HTTP_502_BAD_GATEWAY
    logger.warning("AI Gateway error [%s]: %s", type(exc).__name__, str(exc)[:100])
    return JSONResponse(
        status_code=code,
        content={"detail": "AI service is currently unavailable."},
    )

# Security Headers & Request ID Middleware
@app.middleware("http")
async def add_security_headers_and_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# CORS Middleware
origins = settings.cors_origins_list
if not origins:
    origins = [] # Secure by default

# Allow local testing environments specifically
origins.extend([
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173", # standard react dev port
    "http://localhost:3000",
])

allow_credentials = True
if "*" in origins:
    allow_credentials = False # Cannot use allow_credentials=True when allow_origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=allow_credentials,
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
app.include_router(privacy.router, prefix=f"{settings.API_V1_STR}/privacy", tags=["privacy"])
app.include_router(ai_router_module.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])

@app.get("/")
def root():
    return {"message": "Welcome to ManRakshak API"}

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health():
    return {"status": "ok", "message": "ManRakshak Server is operational"}


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    user_routes,
    auth_routes,
    role_route,
    ticket_route,
    department_route,
    status_route,
    telegram_route,
    notifications_route,
    dashboard_route,
    positions_route,
    staff_route,
    report_route
)
from app.config.db import Base, engine
from dotenv import load_dotenv
from typing import Dict, Any
from fastapi import Depends
from app.middlewares.auth_middlewares import get_current_user

load_dotenv()
app = FastAPI(title="MyApi with Roles & Permissions")

# origin = [
#     "http://localhost:5173",
#     "http://192.168.100.151:5173",
#     "https://wupai.smartdigitalhr.com",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origin,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(role_route.router)
app.include_router(ticket_route.router)
app.include_router(department_route.router)
app.include_router(status_route.router)
app.include_router(telegram_route.router)
app.include_router(notifications_route.router)
app.include_router(dashboard_route.router)
app.include_router(positions_route.router)
app.include_router(staff_route.router)
app.include_router(report_route.router)

app.mount(
    "/uploads",
    StaticFiles(directory="app/uploads"),
    name="uploads",
)


@app.on_event("startup")
def on_startup():
    import app.schema.user_schema
    import app.schema.departments_schema
    import app.schema.role_schema
    import app.schema.permission_schema
    import app.schema.status_schema
    import app.schema.category_schema
    import app.schema.priority_schema
    import app.schema.ticket_schema
    import app.schema.item_schema
    import app.schema.telegram_schema
    import app.schema.notification_schema
    import app.schema.position_schema
    import app.schema.staff_schema

    print("Registered tables before create_all():", list(Base.metadata.tables.keys()))

    # Now create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")


@app.get("/")
def root():
    return {"message": "API running"}


@app.get("/me")
def whoami(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": current_user}

@app.get("/api/health")
def health():
    return {"status": "ok"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes, auth_routes, role_route, ticket_route,department_route
from app.config.db import Base, engine

app = FastAPI(title="MyApi with Roles & Permissions")

origin = [
    "http://192.168.100.151:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(role_route.router)
app.include_router(ticket_route.router)
app.include_router(department_route.router)


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

    print("Registered tables before create_all():", list(Base.metadata.tables.keys()))

    # Now create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")


@app.get("/")
def root():
    return {"message": "API running"}

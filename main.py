from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import accounts, stores, products, orders, deliveries, payments, plans
from config import settings
from database import db

app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(stores.router, prefix="/api/stores", tags=["Stores"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(deliveries.router, prefix="/api/deliveries", tags=["Deliveries"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(plans.router, prefix="/api/plans", tags=["Plans"])

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting FastAPI with GaussDB NoSQL")

@app.on_event("shutdown")
async def shutdown_event():
    db.close()
    print("🔌 Shutdown complete")

@app.get("/")
async def root():
    return {"message": "Latam Store API - Home Delivery for Latin America", "version": settings.version}
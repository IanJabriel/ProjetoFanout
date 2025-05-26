from fastapi import FastAPI
from routes.promocao import router as promocao_router
from database.database import init_db

def create_app():
    app = FastAPI(
        title="API de Promoções",
        description="API para receber e gerenciar promoções",
        version="1.0.0"
    )
    
    init_db()
    
    app.include_router(
        promocao_router,
        prefix="/api",
        tags=["Promoções"]
    )
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
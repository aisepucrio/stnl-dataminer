from fastapi import FastAPI
from src.routes.gh_routes import github_router

app = FastAPI()

# Incluindo as rotas
app.include_router(github_router, prefix="/github")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Data Mining API"}

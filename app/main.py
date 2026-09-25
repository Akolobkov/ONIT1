from fastapi import FastAPI

from app.config import settings
from app.exceptions import BusinessRuleError, business_rule_handler
from app.routers import experiments, models, tasks

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_exception_handler(BusinessRuleError, business_rule_handler)

app.include_router(tasks.router)
app.include_router(models.router)
app.include_router(experiments.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}
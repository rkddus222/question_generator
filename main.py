from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routes import auth, chat, history, report, data
from core.config import settings


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성 및 설정
    """
    app = FastAPI(title="QV API", version="1.0.0")

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(chat.router, tags=["Chat"])
    app.include_router(history.router,tags=["History"])
    app.include_router(report.router, tags=["Reports"])
    app.include_router(data.router, tags=["Data"])

    @app.get("/", include_in_schema=False)
    async def root():
        """건강 체크 엔드포인트"""
        return {"status": "ok", "message": "QV API is running"}

    return app


app = create_app()

if __name__ == "__main__":
    print("\n=== QV run ===")
    uvicorn.run("back.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
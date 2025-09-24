from src.config import settings


def main():
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )


if __name__ == "__main__":
    main()

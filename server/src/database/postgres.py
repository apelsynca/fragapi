from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine(url: str, app_name: str = "FragmentAPI") -> AsyncEngine:
    return create_async_engine(
        url,
        echo=False,
        connect_args={"server_settings": {"application_name": app_name}},
        pool_recycle=600,
    )

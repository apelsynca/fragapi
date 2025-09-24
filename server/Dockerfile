FROM python:3.13-slim-bookworm 

COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

CMD ["uv", "run", "main.py"]

FROM ghcr.io/astral-sh/uv:python3.13-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV ENV development

WORKDIR /category-service

ENV PATH="/category-service/.venv/bin:$PATH"

COPY uv.lock pyproject.toml ./
COPY patches/ ./patches/
RUN uv sync --frozen

EXPOSE 8000
CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]

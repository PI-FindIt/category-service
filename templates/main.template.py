import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import strawberry
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter

from src.api.graphql import Query, Mutation
from src.api.routes import router
from src.api.service import serve_grpc
from src.config.session import init_postgres_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_postgres_db()
    asyncio.create_task(serve_grpc())
    yield


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[OpenTelemetryExtension],
)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="ServiceName", lifespan=lifespan)
app.include_router(router, prefix="/serviceName")
app.include_router(graphql_app, prefix="/serviceName/graphql")

resource = Resource(attributes={SERVICE_NAME: "user-service"})
tracer = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint="apm-server:8200",
    insecure=True,
)
tracer.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer)

FastAPIInstrumentor.instrument_app(app)

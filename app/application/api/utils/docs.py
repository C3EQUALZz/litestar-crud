from typing import TYPE_CHECKING

from dishka.integrations.litestar import FromDishka, inject
from faststream import FastStream
from faststream.asyncapi import get_app_schema, get_asyncapi_html
from faststream.kafka import KafkaBroker
from litestar import MediaType, Router, get

if TYPE_CHECKING:
    from faststream.asyncapi.schema import Schema


@get(media_type=MediaType.HTML)
@inject
async def asyncapi(kafka_broker: FromDishka[KafkaBroker]) -> str:
    schema: Schema = get_app_schema(FastStream(kafka_broker))
    return get_asyncapi_html(schema)


router: Router = Router(path="/docs/asyncapi", route_handlers=[asyncapi])

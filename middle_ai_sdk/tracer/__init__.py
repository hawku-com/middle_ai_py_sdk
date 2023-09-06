import os

from collections.abc import MutableMapping
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span

class Tracer:
    def __init__(self, name: str):
        self._name = name

        endpoint = os.getenv("MIDDLE_AI_ENDPOINT")
        api_key = os.getenv("MIDDLE_AI_API_KEY")

        if endpoint is None:
            self._tracer = None
        else:
            tracer_provider = TracerProvider(
                resource=Resource.create({"service.name": name})
            )

            exporter = OTLPSpanExporter(endpoint=endpoint, headers={"x-middle-ai-api-key": api_key})
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

            self._tracer = trace.get_tracer("MiddleAI", tracer_provider=tracer_provider)

    def start_trace(self, name: str, model: str, model_params: map, prompt: str, user: str, thread_id: str = "") -> Span | None:
        if self._tracer is not None:
            parsed_model_params = self._flatten_dict(model_params)

            attributes = {
                "llm_model": model,
                "enduser_id": user,
                "user_prompt": prompt,
                "application_ref": self._name,
                "thread_id": thread_id
            }

            attributes.update(parsed_model_params)

            return self._tracer.start_span(name, attributes=attributes)

    def end_trace(self, span: Span | None, output: str) -> None:
        if span is not None:
            span.set_attribute("llm_output", output)
            span.end()

    def _flatten_dict(self, model_params: MutableMapping, parent_key: str = '') -> map:
        return dict(self._flatten_dict_gen(model_params, parent_key))

    def _flatten_dict_gen(self, model_params, parent_key) -> map:
        for k, v in model_params.items():
            new_key = parent_key + "." + k if parent_key else k
            if isinstance(v, MutableMapping):
                yield from self._flatten_dict(v, new_key).items()
            else:
                yield new_key, v

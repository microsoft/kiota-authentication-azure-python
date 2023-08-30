from kiota_http.middleware.parameters_name_decoding_handler import ParametersNameDecodingHandler
from kiota_http.observability_options import ObservabilityOptions
from opentelemetry import trace

from ._version import VERSION

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)


class Observability:
    """Helper object to manage creation of spans."""

    def create_parent_span_name(self, uri: str, method: str) -> str:
        """Creates a parent span name for the given method."""
        name_handler = ParametersNameDecodingHandler()
        uri_template = name_handler.decode_uri_encoded_string(uri)
        parent_span_name = f"{method} - {uri_template}"
        return parent_span_name

    def _start_local_tracing_span(self, name: str, parent_span: trace.Span) -> trace.Span:
        """Helper method to start a span locally with the parent context."""
        _context = trace.set_span_in_context(parent_span)
        span = tracer.start_span(name, context=_context)
        return span

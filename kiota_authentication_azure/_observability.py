from kiota_http.middleware.parameters_name_decoding_handler import ParametersNameDecodingHandler
from kiota_http.observability_options import ObservabilityOptions
from opentelemetry import trace

from ._version import VERSION

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)


class Observability:
    """Helper object to manage creation of spans."""

    def start_tracing_span(self, uri: str, method: str) -> trace.Span:
        """Creates an Opentelemetry tracer and starts the parent span.

        Args:
            uri(str): the encoded URI.
            method(str): name of the invoker.

        Returns:
            The parent span.
        """
        name_handler = ParametersNameDecodingHandler()
        uri_template = name_handler.decode_uri_encoded_string(uri)
        parent_span_name = f"{method} - {uri_template}"
        span = tracer.start_span(parent_span_name)
        return span

    def _start_local_tracing_span(self, name: str, parent_span: trace.Span) -> trace.Span:
        """Helper method to start a span locally with the parent context."""
        _context = trace.set_span_in_context(parent_span)
        span = tracer.start_span(name, context=_context)
        return span

class ResponseExecutionError(RuntimeError):
    """Base error raised while generating an assistant response."""


class ResponseConfigurationError(ResponseExecutionError):
    pass


class ResponseAuthenticationError(ResponseExecutionError):
    pass


class ResponseRateLimitError(ResponseExecutionError):
    pass


class ResponseTimeoutError(ResponseExecutionError):
    pass


class ResponseUnavailableError(ResponseExecutionError):
    pass

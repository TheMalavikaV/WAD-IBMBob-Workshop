class ClaimsFlowError(Exception):
    pass


class ValidationError(ClaimsFlowError):
    pass


class NotFoundError(ClaimsFlowError):
    pass


class ConflictError(ClaimsFlowError):
    pass

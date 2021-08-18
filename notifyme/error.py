error_hierarchy = {
    "BaseError": {
        "ValidationError": {
        },
        "AuthenticationError": {
            "AuthFailed": {},
        }
    }
}


class BaseError(Exception):
    pass


class ValidationError(BaseError):
    pass

class AuthenticationError(BaseError):
    pass

class AuthFailed(AuthenticationError):
    pass

__all__ = [
    "error_hierarchy",
    "BaseError",
    "ValidationError",
    "AuthenticationError",
    "AuthFailed"
]

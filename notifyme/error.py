error_hierarchy = {
    "BaseError": {
        "ValidationError":{

        }
    }
}


class BaseError(Exception):
    pass

class ValidationError(BaseError):
    pass


__all__ = [
    "error_hierarchy",
    "BaseError",
    "ValidationError"
]


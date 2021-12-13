from typing import Type


class Error(Exception):
    ...


class ExtractionError(Error):
    ...


class HydrationError(Error):
    def __init__(self, message: str):
        super().__init__(message)


class TypeHydrationError(HydrationError, TypeError):
    def __init__(self, passed: Type, expected: Type):
        self.passed_type = passed
        self.expected_type = expected
        super().__init__(
            f"Could not hydrate value. Expected `{self.expected_type}` type instead of `{self.passed_type}` ."
        )


class UnsupportedTypeError(HydrationError, ValueError):
    def __init__(self, type_name: Type):
        self.type_name = type_name
        super().__init__(
            f"Passed type `{type_name}` is not supported. " f"Please custom hydrator in order to use specified type."
        )


class PropertyError(HydrationError, AttributeError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Could not hydrate value of property `{self.path}`.")


class RequiredPropertyError(PropertyError):
    def __init__(self, path: str):
        self.path = path
        super(Error, self).__init__(f"Could not hydrate value, property `{self.path}` is missing.")

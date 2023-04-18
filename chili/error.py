from gaffe import Error


class SerialisationError(Error):
    invalid_generic_type: TypeError
    strict_type_violation: ValueError
    invalid_type: TypeError
    invalid_input: ValueError


class DecoderError(SerialisationError):
    ...


class EncoderError(SerialisationError):
    encoding_failed = ...


class MapperError(SerialisationError):
    invalid_schema: ValueError
    invalid_value: ValueError

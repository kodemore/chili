PWD := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
.DEFAULT_GOAL := all

benchmark:
	hyperfine --export-markdown README.md \
		'poetry run python --version'\
		'poetry run python benchmarks/chili_decode.py'\
		'poetry run python benchmarks/pydantic_decode.py'\
		'poetry run python benchmarks/attrs_decode.py'\
		'poetry run python benchmarks/marshmallow_decode.py'\
		'poetry run python benchmarks/chili_encode.py'\
		'poetry run python benchmarks/pydantic_encode.py'\
		'poetry run python benchmarks/attrs_encode.py'\
		'poetry run python benchmarks/marshmallow_encode.py'\

version:
	poetry version

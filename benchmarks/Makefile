PWD := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
.DEFAULT_GOAL := all

benchmark:
	hyperfine --export-markdown results.md \
		'poetry run python benchmarks/chili_decode.py'\
		'poetry run python benchmarks/pydantic_decode.py'\
		'poetry run python benchmarks/attrs_decode.py'\
		'poetry run python benchmarks/chili_encode.py'\
		'poetry run python benchmarks/pydantic_encode.py'\
		'poetry run python benchmarks/attrs_encode.py'\

version:
	poetry version

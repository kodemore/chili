| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `poetry run python --version` | 271.6 ± 39.1 | 251.6 | 381.0 | 1.00 |
| `poetry run python benchmarks/chili_decode.py` | 293.0 ± 5.6 | 287.4 | 305.9 | 1.08 ± 0.16 |
| `poetry run python benchmarks/pydantic_decode.py` | 346.7 ± 18.0 | 330.3 | 386.3 | 1.28 ± 0.20 |
| `poetry run python benchmarks/attrs_decode.py` | 305.2 ± 7.2 | 297.6 | 321.9 | 1.12 ± 0.16 |
| `poetry run python benchmarks/marshmallow_decode.py` | 304.1 ± 4.4 | 299.2 | 314.0 | 1.12 ± 0.16 |
| `poetry run python benchmarks/chili_encode.py` | 295.9 ± 5.1 | 285.6 | 303.3 | 1.09 ± 0.16 |
| `poetry run python benchmarks/pydantic_encode.py` | 342.7 ± 8.2 | 328.6 | 356.8 | 1.26 ± 0.18 |
| `poetry run python benchmarks/attrs_encode.py` | 303.5 ± 7.3 | 291.0 | 314.5 | 1.12 ± 0.16 |
| `poetry run python benchmarks/marshmallow_encode.py` | 301.2 ± 4.2 | 292.8 | 308.6 | 1.11 ± 0.16 |

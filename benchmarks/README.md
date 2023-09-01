| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `poetry run python benchmarks/chili_decode.py` | 246.4 ± 1.6 | 244.8 | 249.6 | 1.00 |
| `poetry run python benchmarks/pydantic_decode.py` | 288.2 ± 1.8 | 284.5 | 291.0 | 1.17 ± 0.01 |
| `poetry run python benchmarks/attrs_decode.py` | 256.6 ± 1.8 | 253.3 | 259.5 | 1.04 ± 0.01 |
| `poetry run python benchmarks/marshmallow_decode.py` | 256.8 ± 5.4 | 252.2 | 271.0 | 1.04 ± 0.02 |
| `poetry run python benchmarks/chili_encode.py` | 248.8 ± 4.2 | 243.6 | 256.5 | 1.01 ± 0.02 |
| `poetry run python benchmarks/pydantic_encode.py` | 298.0 ± 14.4 | 288.3 | 325.7 | 1.21 ± 0.06 |
| `poetry run python benchmarks/attrs_encode.py` | 257.9 ± 3.6 | 252.6 | 263.4 | 1.05 ± 0.02 |
| `poetry run python benchmarks/marshmallow_encode.py` | 254.0 ± 2.7 | 250.9 | 260.6 | 1.03 ± 0.01 |

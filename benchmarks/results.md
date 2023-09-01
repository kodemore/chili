| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `poetry run python benchmarks/chili_decode.py` | 249.4 ± 4.1 | 245.5 | 258.8 | 1.01 ± 0.02 |
| `poetry run python benchmarks/pydantic_decode.py` | 295.5 ± 12.5 | 287.6 | 327.1 | 1.19 ± 0.05 |
| `poetry run python benchmarks/attrs_decode.py` | 260.9 ± 8.6 | 253.2 | 283.5 | 1.05 ± 0.04 |
| `poetry run python benchmarks/chili_encode.py` | 247.8 ± 2.3 | 245.4 | 253.0 | 1.00 |
| `poetry run python benchmarks/pydantic_encode.py` | 292.4 ± 4.7 | 287.1 | 302.5 | 1.18 ± 0.02 |
| `poetry run python benchmarks/attrs_encode.py` | 258.2 ± 2.1 | 254.4 | 261.4 | 1.04 ± 0.01 |

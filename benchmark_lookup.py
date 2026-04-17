import timeit
from src.scanning_tool.deposits.lookup import _parse_alphanumeric_code


def run_benchmark():
    setup = "from src.scanning_tool.deposits.lookup import _parse_alphanumeric_code"
    code = "_parse_alphanumeric_code('A-123,456.78')"
    # Warmup
    timeit.timeit(code, setup=setup, number=1000)

    # Benchmark
    times = timeit.repeat(code, setup=setup, number=100000, repeat=5)
    best_time = min(times)
    print(f"Best time for 100,000 iterations: {best_time:.4f} seconds")


if __name__ == "__main__":
    run_benchmark()



import time
import statistics
import csv
from Matrix import make_random_matrix, multiply_naive, multiply_blocked, multiply_numpy

IMPLEMENTATIONS = {
    "naive": multiply_naive,
    "blocked": multiply_blocked,
    "numpy": multiply_numpy,
}

SIZES = [64, 128, 256, 512]
REPEATS = 5
BLOCK_SIZE = 32
CSV_FILE = "/Users/rafasuarzz/Documents/IndividualAssignment/Results/results_python.csv"  # poner None si no quieres CSV
# ----------------------------------------------------------------------


def run_once(impl_name, n, block):
    A = make_random_matrix(n, seed=123)
    B = make_random_matrix(n, seed=456)
    impl = IMPLEMENTATIONS[impl_name]
    start = time.perf_counter()
    if impl_name == "blocked":
        impl(A, B, block)
    else:
        impl(A, B)
    end = time.perf_counter()
    return end - start


def benchmark(impl_name, n, repeats, block=32):
    times = []
    for r in range(repeats):
        t = run_once(impl_name, n, block)
        times.append(t)
    return times


def pretty_print(name, n, times):
    """Imprime y devuelve estadísticas resumidas."""
    mean = statistics.mean(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    print(f"Impl={name}, n={n}, runs={len(times)}")
    print(f"  min={min(times):.6f}s mean={mean:.6f}s std={std:.6f}s max={max(times):.6f}s\n")
    return mean, std, min(times), max(times)


def main():
    results = []
    print("\n=== Benchmarking all implementations ===\n")

    for impl in IMPLEMENTATIONS.keys():
        print(f"--- {impl.upper()} IMPLEMENTATION ---")
        for n in SIZES:
            times = benchmark(impl, n, REPEATS, BLOCK_SIZE)
            mean, std, tmin, tmax = pretty_print(impl, n, times)
            results.append({
                "impl": impl,
                "n": n,
                "mean": mean,
                "std": std,
                "min": tmin,
                "max": tmax
            })
        print("-" * 60)

    if CSV_FILE:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["impl", "n", "mean", "std", "min", "max"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Resultados guardados en {CSV_FILE}\n")


if __name__ == "__main__":
    main()

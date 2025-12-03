import numpy as np
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def matmul_vectorized(A, B):
    return A @ B

def _row_worker(i, A_row, B, sem, counter_lock, counter):
    with sem:
        row_res = np.dot(A_row, B)
    with counter_lock:
        counter[0] += 1
    return (i, row_res)

def matmul_parallel_semaphore(A, B, max_workers=None, max_concurrent=None):
    n = A.shape[0]
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    if max_concurrent is None:
        max_concurrent = max(1, (os.cpu_count() or 1))

    sem = threading.Semaphore(max_concurrent)
    counter_lock = threading.Lock()
    counter = [0]

    C = np.zeros((n, B.shape[1]), dtype=A.dtype)
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for i in range(n):
            futures.append(ex.submit(_row_worker, i, A[i, :], B, sem, counter_lock, counter))

        for fut in as_completed(futures):
            i, row_res = fut.result()
            C[i, :] = row_res

    return C, counter[0]

def bench_and_compare(sizes, repeats=1, max_workers=None, max_concurrent=None):
    for n in sizes:
        est_bytes = 8 * (n * n * 3)
        est_mb = est_bytes / (1024**2)
        print(f"\n=== Size {n}x{n} (≈ {est_mb:.1f} MB) ===")
        if est_mb > 8000:
            print("  WARNING: Matrix too large, possible OOM. Skipping.")
            continue

        A = np.random.rand(n, n).astype(np.float64)
        B = np.random.rand(n, n).astype(np.float64)

        t_start = time.perf_counter()
        C_par, done = matmul_parallel_semaphore(A, B, max_workers=max_workers, max_concurrent=max_concurrent)
        t_par = time.perf_counter() - t_start
        print(f"Parallel:    {t_par:.4f} s  (rows processed: {done})")

        t_start = time.perf_counter()
        C_vec = matmul_vectorized(A, B)
        t_vec = time.perf_counter() - t_start
        print(f"Vectorized:  {t_vec:.4f} s")

        maxdiff = np.max(np.abs(C_par - C_vec))
        print(f"Max abs diff: {maxdiff:.3e}")
        print(f"Speedup vectorized/parallel: {t_par / t_vec:.2f}x")

if __name__ == "__main__":
    SIZES = [100, 500, 1000, 5000]
    MAX_WORKERS = None
    MAX_CONCURRENT = None
    bench_and_compare(SIZES)

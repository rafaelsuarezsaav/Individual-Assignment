
"""
matrix multiplication implementations.
Production code only (no CLI / benchmarking code here).
"""

from typing import List, Callable, Optional
import random

matrix = List[List[float]]

def make_random_matrix(n: int, seed: Optional[int]=None) -> matrix:
    if seed is not None:
        random.seed(seed)
    return [[random.random() for _ in range(n)] for _ in range(n)]

def zero_matrix(n: int) -> matrix:
    return [[0.0 for _ in range(n)] for _ in range(n)]

def multiply_naive(A: matrix, B: matrix) -> matrix:
    n = len(A)
    C = zero_matrix(n)
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for k in range(n):
            Aik = Ai[k]
            Bk = B[k]
            for j in range(n):
                Ci[j] += Aik * Bk[j]
    return C

def multiply_blocked(A: matrix, B: matrix, block: int=32) -> matrix:
    n = len(A)
    C = zero_matrix(n)
    for ii in range(0, n, block):
        for kk in range(0, n, block):
            for jj in range(0, n, block):
                i_max = min(ii+block, n)
                k_max = min(kk+block, n)
                j_max = min(jj+block, n)
                for i in range(ii, i_max):
                    for k in range(kk, k_max):
                        Aik = A[i][k]
                        rowC = C[i]
                        rowB = B[k]
                        for j in range(jj, j_max):
                            rowC[j] += Aik * rowB[j]
    return C

def multiply_numpy(A, B):
    try:
        import numpy as np
    except ImportError:
        raise RuntimeError("numpy not installed")
    return (np.dot(A, B)).tolist()

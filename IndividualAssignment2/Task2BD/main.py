import numpy as np
import time
from threading import Thread


# --- Clase CSR ---
class CSRMatrix:
    def __init__(self, data, indices, indptr, shape):
        self.data = data
        self.indices = indices
        self.indptr = indptr
        self.shape = shape


# --- Función para generar matrices aleatorias CSR ---
def generate_random_csr(n_rows, n_cols, sparsity):
    """
    n_rows: filas
    n_cols: columnas
    sparsity: porcentaje de ceros (0 a 1)
    """
    nnz_per_row = max(1, int(n_cols * (1 - sparsity)))  # no dejar fila vacía
    data = []
    indices = []
    indptr = [0]

    for i in range(n_rows):
        cols = np.random.choice(n_cols, nnz_per_row, replace=False)
        vals = np.random.rand(nnz_per_row)
        indices.extend(cols)
        data.extend(vals)
        indptr.append(len(indices))

    return CSRMatrix(np.array(data), np.array(indices), np.array(indptr), (n_rows, n_cols))


# --- SpMV clásico ---
def spmv_csr(matrix, x):
    y = np.zeros(matrix.shape[0])
    for i in range(matrix.shape[0]):
        start, end = matrix.indptr[i], matrix.indptr[i + 1]
        y[i] = np.dot(matrix.data[start:end], x[matrix.indices[start:end]])
    return y


# --- SpMV con bucle optimizado ---
def spmv_csr_loop(matrix, x):
    y = np.zeros(matrix.shape[0])
    for i in range(matrix.shape[0]):
        s = 0.0
        start, end = matrix.indptr[i], matrix.indptr[i + 1]
        for j in range(start, end):
            s += matrix.data[j] * x[matrix.indices[j]]
        y[i] = s
    return y


# --- SpMV multithread básico ---
def spmv_csr_thread(matrix, x, num_threads=2):
    y = np.zeros(matrix.shape[0])

    def worker(start_row, end_row):
        for i in range(start_row, end_row):
            s = 0.0
            for j in range(matrix.indptr[i], matrix.indptr[i + 1]):
                s += matrix.data[j] * x[matrix.indices[j]]
            y[i] = s

    threads = []
    rows_per_thread = matrix.shape[0] // num_threads
    for t in range(num_threads):
        start = t * rows_per_thread
        end = matrix.shape[0] if t == num_threads - 1 else (t + 1) * rows_per_thread
        threads.append(Thread(target=worker, args=(start, end)))
        threads[-1].start()

    for t in threads:
        t.join()

    return y


# --- Ejemplo de ejecución con diferentes tamaños y sparsity ---
matrix_sizes = [(100, 100), (500, 500), (1000, 1000), (10000, 10000)]
sparsities = [0.5, 0.8, 0.9, 0.95]

for size in matrix_sizes:
    for sp in sparsities:
        print(f"\nMatrix {size} with sparsity {sp}")
        A = generate_random_csr(size[0], size[1], sp)
        x = np.random.rand(size[1])

        start = time.time()
        y_basic = spmv_csr(A, x)
        print("Basic CSR Time:", round(time.time() - start, 4), "s")

        start = time.time()
        y_loop = spmv_csr_loop(A, x)
        print("Optimized Loop CSR Time:", round(time.time() - start, 4), "s")

        start = time.time()
        y_thread = spmv_csr_thread(A, x, num_threads=4)
        print("Multithread CSR Time:", round(time.time() - start, 4), "s")

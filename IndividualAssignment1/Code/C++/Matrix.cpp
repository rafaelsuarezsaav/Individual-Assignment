#include "Matrix.h"
#include <random>
#include <algorithm>

Matrix random_matrix(int n, unsigned seed) {
    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    Matrix M(n, std::vector<double>(n));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            M[i][j] = dist(rng);
    return M;
}

Matrix zero_matrix(int n) {
    return Matrix(n, std::vector<double>(n, 0.0));
}

Matrix naive_multiply(const Matrix &A, const Matrix &B) {
    int n = (int)A.size();
    Matrix C = zero_matrix(n);
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            double aik = A[i][k];
            for (int j = 0; j < n; j++) {
                C[i][j] += aik * B[k][j];
            }
        }
    }
    return C;
}

Matrix blocked_multiply(const Matrix &A, const Matrix &B, int block) {
    int n = (int)A.size();
    Matrix C = zero_matrix(n);
    for (int ii = 0; ii < n; ii += block) {
        for (int kk = 0; kk < n; kk += block) {
            for (int jj = 0; jj < n; jj += block) {
                int iMax = std::min(ii + block, n);
                int kMax = std::min(kk + block, n);
                int jMax = std::min(jj + block, n);
                for (int i = ii; i < iMax; i++) {
                    for (int k = kk; k < kMax; k++) {
                        double aik = A[i][k];
                        for (int j = jj; j < jMax; j++) {
                            C[i][j] += aik * B[k][j];
                        }
                    }
                }
            }
        }
    }
    return C;
}

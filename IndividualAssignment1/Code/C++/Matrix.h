#ifndef MATRIX_H
#define MATRIX_H

#include <vector>

using Matrix = std::vector<std::vector<double>>;

Matrix random_matrix(int n, unsigned seed);
Matrix zero_matrix(int n);
Matrix naive_multiply(const Matrix &A, const Matrix &B);
Matrix blocked_multiply(const Matrix &A, const Matrix &B, int block=32);

#endif

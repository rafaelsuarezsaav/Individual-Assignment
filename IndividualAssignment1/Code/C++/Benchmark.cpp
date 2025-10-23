#include "Matrix.h"
#include <chrono>
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <fstream>
#include <algorithm>
#include <string>

int main() {
    // -----------------------------------------------------
    // Configuración general (puedes modificar aquí)
    // -----------------------------------------------------
    std::vector<int> sizes = {64, 128, 256, 512}; // tamaños de las matrices
    int repeats = 5;                              // repeticiones por tamaño
    int block = 32;                               // tamaño de bloque
    std::vector<std::string> impls = {"naive", "blocked"};
    std::string csv_file = "/Users/rafasuarzz/Documents/IndividualAssignment/Results/results_cpp.csv";     // poner "" si no quieres CSV
    // -----------------------------------------------------

    std::cout << "\n=== Benchmarking all C++ implementations ===\n" << std::endl;

    std::ofstream csv;
    if (!csv_file.empty()) {
        csv.open(csv_file);
        csv << "impl,n,mean,std,min,max\n";
    }

    for (const auto& impl : impls) {
        std::cout << "--- " << impl << " IMPLEMENTATION ---" << std::endl;

        for (int n : sizes) {
            std::vector<double> times;
            times.reserve(repeats);

            for (int r = 0; r < repeats; r++) {
                auto A = random_matrix(n, 1000 + r);
                auto B = random_matrix(n, 2000 + r);

                auto t0 = std::chrono::high_resolution_clock::now();
                if (impl == "blocked") {
                    blocked_multiply(A, B, block);
                } else {
                    naive_multiply(A, B);
                }
                auto t1 = std::chrono::high_resolution_clock::now();
                std::chrono::duration<double> diff = t1 - t0;
                times.push_back(diff.count());
            }

            double sum = 0;
            for (double v : times) sum += v;
            double mean = sum / times.size();
            double variance = 0;
            for (double v : times) variance += (v - mean) * (v - mean);
            variance /= times.size();
            double stddev = std::sqrt(variance);
            double min_time = *std::min_element(times.begin(), times.end());
            double max_time = *std::max_element(times.begin(), times.end());

            std::cout << "Impl=" << impl
                      << ", n=" << n
                      << ", runs=" << repeats << std::endl;
            std::cout << "  min=" << std::fixed << std::setprecision(6) << min_time
                      << "s mean=" << mean
                      << "s std=" << stddev
                      << "s max=" << max_time << "s\n" << std::endl;

            if (csv.is_open()) {
                csv << impl << "," << n << ","
                    << mean << "," << stddev << ","
                    << min_time << "," << max_time << "\n";
            }
        }
        std::cout << "----------------------------------------------------\n" << std::endl;
    }

    if (csv.is_open()) {
        csv.close();
        std::cout << "Resultados guardados en " << csv_file << std::endl;
    }

    return 0;
}

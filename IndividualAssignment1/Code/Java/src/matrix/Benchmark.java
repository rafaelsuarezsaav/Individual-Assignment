package matrix;

import java.util.Arrays;
import java.io.FileWriter;
import java.io.IOException;

public class Benchmark {

    // Configuración global
    static final int[] SIZES = {64, 128, 256, 512};   // tamaños de las matrices
    static final int REPEATS = 5;                     // repeticiones por tamaño
    static final int BLOCK_SIZE = 32;                 // tamaño de bloque para 'blocked'
    static final String[] IMPLEMENTATIONS = {"naive", "blocked"}; // versiones a probar
    static final String CSV_FILE = "/Users/rafasuarzz/Documents/IndividualAssignment/Results/results_java.csv"; // CSV de salida (pon null si no quieres archivo)

    public static void main(String[] args) {
        System.out.println("\n=== Benchmarking all Java implementations ===\n");
        StringBuilder csv = new StringBuilder("impl,n,mean,std,min,max\n");

        for (String impl : IMPLEMENTATIONS) {
            System.out.println("--- " + impl.toUpperCase() + " IMPLEMENTATION ---");

            for (int n : SIZES) {
                double[] times = new double[REPEATS];

                for (int r = 0; r < REPEATS; r++) {
                    double[][] A = Matrix.randomMatrix(n, 1234L + r);
                    double[][] B = Matrix.randomMatrix(n, 2345L + r);

                    long t0 = System.nanoTime();
                    if (impl.equals("blocked")) {
                        Matrix.blockedMultiply(A, B, BLOCK_SIZE);
                    } else {
                        Matrix.naiveMultiply(A, B);
                    }
                    long t1 = System.nanoTime();
                    times[r] = (t1 - t0) / 1e9;
                }

                double mean = mean(times);
                double std = stddev(times, mean);
                double min = Arrays.stream(times).min().getAsDouble();
                double max = Arrays.stream(times).max().getAsDouble();

                System.out.printf("Impl=%s, n=%d, runs=%d\n", impl, n, REPEATS);
                System.out.printf("  min=%.6fs mean=%.6fs std=%.6fs max=%.6fs\n\n",
                        min, mean, std, max);

                csv.append(String.format("%s,%d,%.6f,%.6f,%.6f,%.6f\n",
                        impl, n, mean, std, min, max));
            }
            System.out.println("----------------------------------------------------\n");
        }

        // Guardar resultados en CSV
        if (CSV_FILE != null) {
            try (FileWriter fw = new FileWriter(CSV_FILE)) {
                fw.write(csv.toString());
                System.out.println("Results saved " + CSV_FILE);
            } catch (IOException e) {
                System.err.println("Error writing CSV: " + e.getMessage());
            }
        }
    }
    private static double mean(double[] arr) {
        double sum = 0;
        for (double v : arr) sum += v;
        return sum / arr.length;
    }

    private static double stddev(double[] arr, double mean) {
        double sum = 0;
        for (double v : arr) {
            double diff = v - mean;
            sum += diff * diff;
        }
        return Math.sqrt(sum / arr.length);
    }
}

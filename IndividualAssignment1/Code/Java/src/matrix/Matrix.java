package matrix;

import java.util.Random;

public class Matrix {
    public static double[][] randomMatrix(int n, long seed) {
        Random r = new Random(seed);
        double[][] M = new double[n][n];
        for (int i=0;i<n;i++){
            for (int j=0;j<n;j++){
                M[i][j] = r.nextDouble();
            }
        }
        return M;
    }

    public static double[][] zeroMatrix(int n) {
        return new double[n][n];
    }

    public static double[][] naiveMultiply(double[][] A, double[][] B) {
        int n = A.length;
        double[][] C = zeroMatrix(n);
        for (int i=0;i<n;i++){
            for (int k=0;k<n;k++){
                double aik = A[i][k];
                for (int j=0;j<n;j++){
                    C[i][j] += aik * B[k][j];
                }
            }
        }
        return C;
    }

    // blocking version
    public static double[][] blockedMultiply(double[][] A, double[][] B, int block) {
        int n = A.length;
        double[][] C = zeroMatrix(n);
        for (int ii=0; ii<n; ii+=block) {
            for (int kk=0; kk<n; kk+=block) {
                for (int jj=0; jj<n; jj+=block) {
                    int iMax = Math.min(ii+block, n);
                    int kMax = Math.min(kk+block, n);
                    int jMax = Math.min(jj+block, n);
                    for (int i=ii; i<iMax; i++) {
                        for (int k=kk; k<kMax; k++) {
                            double aik = A[i][k];
                            for (int j=jj; j<jMax; j++) {
                                C[i][j] += aik * B[k][j];
                            }
                        }
                    }
                }
            }
        }
        return C;
    }
}



public final class BlockOps {

    private BlockOps() {}

    public static double[] createEmpty(int blockSize) {
        return new double[blockSize * blockSize];
    }

    public static void accumulate(double[] dst,
                                  double[] left,
                                  double[] right,
                                  int blockSize) {

        for (int i = 0; i < blockSize; i++) {
            int iOffset = i * blockSize;

            for (int k = 0; k < blockSize; k++) {
                double value = left[iOffset + k];
                if (value == 0.0) {
                    continue;
                }

                int kOffset = k * blockSize;
                for (int j = 0; j < blockSize; j++) {
                    dst[iOffset + j] += value * right[kOffset + j];
                }
            }
        }
    }

    public static String composeKey(int rowBlock, int colBlock) {
        return rowBlock + "," + colBlock;
    }
}

import com.hazelcast.client.HazelcastClient;
import com.hazelcast.client.config.ClientConfig;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.IExecutorService;
import com.hazelcast.map.IMap;

import java.io.*;
import java.util.*;
import java.util.concurrent.Future;

public final class DriverMain {

    private static final String MAP_A = "A_blocks";
    private static final String MAP_B = "B_blocks";
    private static final String MAP_C = "C_blocks";
    private static final String EXECUTOR = "mm-exec";

    public static void main(String[] args) throws Exception {
        Args parameters = Args.parse(args);

        ClientConfig clientConfig = new ClientConfig();
        clientConfig.setClusterName("mm-cluster");
        HazelcastInstance client = HazelcastClient.newHazelcastClient(clientConfig);

        try {
            IMap<String, double[]> mapA = client.getMap(MAP_A);
            IMap<String, double[]> mapB = client.getMap(MAP_B);
            IMap<String, double[]> mapC = client.getMap(MAP_C);

            mapA.clear();
            mapB.clear();
            mapC.clear();

            loadBlocksFromFile(parameters.aPath, 'A', parameters.blockSize, mapA);
            loadBlocksFromFile(parameters.bPath, 'B', parameters.blockSize, mapB);

            IExecutorService executor = client.getExecutorService(EXECUTOR);
            List<Future<String>> taskFutures = new ArrayList<>();

            for (int row = 0; row < parameters.numBlocks; row++) {
                for (int col = 0; col < parameters.numBlocks; col++) {
                    BlockComputationTask task = new BlockComputationTask(
                            row, col, parameters.numBlocks, parameters.blockSize,
                            MAP_A, MAP_B, MAP_C
                    );
                    taskFutures.add(executor.submit(task));
                }
            }

            for (Future<String> f : taskFutures) {
                f.get();
            }

            writeCBlocksToFile(parameters.outPath, parameters.blockSize, parameters.numBlocks, mapC);

        } finally {
            client.shutdown();
        }
    }

    private static void loadBlocksFromFile(String path, char tag, int blockSize, IMap<String, double[]> target) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) continue;
                String[] tokens = line.split(",");
                if (tokens.length < 3) continue;

                char currentTag = tokens[0].trim().charAt(0);
                if (currentTag != tag) continue;

                int x = Integer.parseInt(tokens[1].trim());
                int y = Integer.parseInt(tokens[2].trim());

                int expectedLength = blockSize * blockSize;
                double[] values = new double[expectedLength];
                for (int idx = 0; idx < expectedLength; idx++) {
                    values[idx] = Double.parseDouble(tokens[3 + idx]);
                }

                target.set(BlockOps.composeKey(x, y), values);
            }
        }
    }

    private static void writeCBlocksToFile(String path, int blockSize, int numBlocks, IMap<String, double[]> mapC) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(path))) {
            for (int i = 0; i < numBlocks; i++) {
                for (int j = 0; j < numBlocks; j++) {
                    String key = BlockOps.composeKey(i, j);
                    double[] block = mapC.get(key);
                    if (block == null) {
                        block = BlockOps.createEmpty(blockSize);
                    }

                    StringBuilder sb = new StringBuilder();
                    sb.append("C").append(",").append(i).append(",").append(j);
                    for (double v : block) {
                        sb.append(",").append(formatDouble(v));
                    }
                    writer.write(sb.toString());
                    writer.newLine();
                }
            }
        }
    }

    private static String formatDouble(double value) {
        return String.format(Locale.US, "%.10g", value);
    }

    private static final class Args {
        final String aPath;
        final String bPath;
        final String outPath;
        final int blockSize;
        final int numBlocks;

        private Args(String aPath, String bPath, String outPath, int blockSize, int numBlocks) {
            this.aPath = aPath;
            this.bPath = bPath;
            this.outPath = outPath;
            this.blockSize = blockSize;
            this.numBlocks = numBlocks;
        }

        static Args parse(String[] argv) {
            Map<String, String> argsMap = new HashMap<>();
            for (int i = 0; i < argv.length; i++) {
                if (argv[i].startsWith("--") && i + 1 < argv.length) {
                    argsMap.put(argv[i], argv[i + 1]);
                    i++;
                }
            }

            String a = requireArg(argsMap, "--a");
            String b = requireArg(argsMap, "--b");
            String out = requireArg(argsMap, "--out");
            int bs = Integer.parseInt(requireArg(argsMap, "--block-size"));
            int nb = Integer.parseInt(requireArg(argsMap, "--num-blocks"));

            return new Args(a, b, out, bs, nb);
        }

        static String requireArg(Map<String, String> map, String key) {
            String value = map.get(key);
            if (value == null) throw new IllegalArgumentException("Missing argument: " + key);
            return value;
        }
    }
}

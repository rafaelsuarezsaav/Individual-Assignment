import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.HazelcastInstanceAware;
import com.hazelcast.map.IMap;



import java.io.Serializable;
import java.util.concurrent.Callable;

public final class BlockComputationTask implements Callable<String>, Serializable, HazelcastInstanceAware {

    private final int rowBlock;
    private final int colBlock;
    private final int totalBlocks;
    private final int blockSize;

    private final String nameMapA;
    private final String nameMapB;
    private final String nameMapC;

    private transient HazelcastInstance hzInstance;

    public BlockComputationTask(int rowBlock, int colBlock, int totalBlocks, int blockSize,
                                String nameMapA, String nameMapB, String nameMapC) {
        this.rowBlock = rowBlock;
        this.colBlock = colBlock;
        this.totalBlocks = totalBlocks;
        this.blockSize = blockSize;
        this.nameMapA = nameMapA;
        this.nameMapB = nameMapB;
        this.nameMapC = nameMapC;
    }

    @Override
    public void setHazelcastInstance(HazelcastInstance hazelcastInstance) {
        this.hzInstance = hazelcastInstance;
    }

    @Override
    public String call() {
        if (hzInstance == null) throw new IllegalStateException("Hazelcast instance not available");

        IMap<String, double[]> mapA = hzInstance.getMap(nameMapA);
        IMap<String, double[]> mapB = hzInstance.getMap(nameMapB);
        IMap<String, double[]> mapC = hzInstance.getMap(nameMapC);

        double[] resultBlock = BlockOps.createEmpty(blockSize);

        for (int k = 0; k < totalBlocks; k++) {
            double[] aBlock = mapA.get(BlockOps.composeKey(rowBlock, k));
            double[] bBlock = mapB.get(BlockOps.composeKey(k, colBlock));

            if (aBlock != null && bBlock != null) {
                BlockOps.accumulate(resultBlock, aBlock, bBlock, blockSize);
            }
        }

        String key = BlockOps.composeKey(rowBlock, colBlock);
        mapC.set(key, resultBlock);
        return key;
    }
}

import com.hazelcast.config.Config;
import com.hazelcast.config.JoinConfig;
import com.hazelcast.core.Hazelcast;

public class MemberMain {
    public static void main(String[] args) {
        Config config = new Config();
        config.setClusterName("mm-cluster");

        JoinConfig join = config.getNetworkConfig().getJoin();
        join.getMulticastConfig().setEnabled(false);
        join.getTcpIpConfig()
                .setEnabled(true)
                .addMember("127.0.0.1");

        Hazelcast.newHazelcastInstance(config);
        System.out.println("Hazelcast member started.");
    }
}

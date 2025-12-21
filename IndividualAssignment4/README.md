# Distributed Blocked Matrix Multiplication – Task 4

This project contains **two distributed execution variants** for blocked dense matrix multiplication:

- **Python (local MapReduce runner)** – simulates a MapReduce workflow on a single machine using Python scripts.
- **Java (Hazelcast distributed execution)** – executes on a real cluster using Hazelcast in-memory data grids.

Both variants use the **same block-CSV format**:

- `A,iBlock,kBlock,v0,v1,...,v(b*b-1)`
- `B,kBlock,jBlock,v0,v1,...,v(b*b-1)`
- `C,iBlock,jBlock,v0,v1,...,v(b*b-1)`

Blocks are stored in row-major order. Edge blocks are zero-padded when `N` is not divisible by `blockSize`.

---

## Python – Local MapReduce Runner

### Generate Input Blocks


python3 matrix_block_tools.py gen --n 256 --block-size 64 --out-a A.csv --out-b B.csv
Generates CSV files for matrices A and B divided into blocks.

Run MapReduce Locally

python3 mapreduce_runner.py --num-blocks 4 --block-size 64 A.csv B.csv --out C.csv
Executes mapper, shuffle, and reducer to produce C.csv.

Verify Output

python3 matrix_block_tools.py verify --n 256 --block-size 64 --c-blocks C.csv
Reconstructs the full matrix C and prints the top-left 5x5 submatrix.

Java – Hazelcast Distributed Execution
Requires Java 17+.



mvn -DskipTests package

Creates a runnable JAR in target/hz-mm-1.0.0.jar.

Start Hazelcast Members (2 Terminals)
Terminal 1:
java -cp target/hz-mm-1.0.0.jar MemberMain

Terminal 2:
java -cp target/hz-mm-1.0.0.jar MemberMain
This starts a 2-node Hazelcast cluster on localhost.

Generate Input Blocks
Use the Python utility:

python3 matrix_block_tools.py gen --n 256 --block-size 64 --out-a A.csv --out-b B.csv

Run Hazelcast Driver

java -cp target/hz-mm-1.0.0.jar DriverMain --a ../A.csv --b ../B.csv --out ../C_hz.csv --block-size 64 --num-blocks 4

Loads A and B blocks into distributed IMaps, submits tasks for each output block, and writes C_hz.csv.

Verify Output
python3 matrix_block_tools.py verify --n 256 --block-size 64 --c-blocks C_hz.csv
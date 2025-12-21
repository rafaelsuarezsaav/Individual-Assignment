#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import random
from typing import List, Dict, Tuple


def make_zero_matrix(size: int) -> List[List[float]]:
    return [[0.0 for _ in range(size)] for _ in range(size)]


def random_matrix(size: int, seed: int) -> List[List[float]]:
    rng = random.Random(seed)
    return [[rng.uniform(0.0, 10.0) for _ in range(size)] for _ in range(size)]


def export_blocks(matrix: List[List[float]],
                  label: str,
                  block_size: int,
                  filename: str) -> None:
    dim = len(matrix)
    blocks = math.ceil(dim / block_size)

    with open(filename, "w", newline="") as fh:
        writer = csv.writer(fh)
        for bi in range(blocks):
            for bj in range(blocks):
                flat_block: List[float] = []
                base_i = bi * block_size
                base_j = bj * block_size
                for r in range(block_size):
                    for c in range(block_size):
                        i = base_i + r
                        j = base_j + c
                        if i < dim and j < dim:
                            flat_block.append(matrix[i][j])
                        else:
                            flat_block.append(0.0)
                writer.writerow([label, bi, bj, *flat_block])


def load_blocks(path: str,
                block_size: int) -> Dict[Tuple[int, int], List[float]]:
    data: Dict[Tuple[int, int], List[float]] = {}

    with open(path, newline="") as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue

            tag = row[0].strip()
            if tag not in {"A", "B", "C"}:
                continue

            bi = int(row[1])
            bj = int(row[2])
            values = list(map(float, row[3:]))

            expected = block_size * block_size
            if len(values) != expected:
                raise ValueError(
                    f"Invalid block length: expected {expected}, got {len(values)}"
                )

            data[(bi, bj)] = values

    return data


def assemble_matrix(blocks: Dict[Tuple[int, int], List[float]],
                    size: int,
                    block_size: int) -> List[List[float]]:
    matrix = make_zero_matrix(size)

    for (bi, bj), block in blocks.items():
        base_i = bi * block_size
        base_j = bj * block_size
        for r in range(block_size):
            for c in range(block_size):
                i = base_i + r
                j = base_j + c
                if i < size and j < size:
                    matrix[i][j] = block[r * block_size + c]

    return matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)

    gen = subparsers.add_parser(
        "gen", help="Generate random matrices and export block CSV files"
    )
    gen.add_argument("--n", type=int, required=True)
    gen.add_argument("--block-size", type=int, default=64)
    gen.add_argument("--seed", type=int, default=1)
    gen.add_argument("--out-a", default="A_blocks.csv")
    gen.add_argument("--out-b", default="B_blocks.csv")

    chk = subparsers.add_parser(
        "verify", help="Rebuild matrix C from block CSV and display a preview"
    )
    chk.add_argument("--n", type=int, required=True)
    chk.add_argument("--block-size", type=int, default=64)
    chk.add_argument("--c-blocks", required=True)

    args = parser.parse_args()

    if args.mode == "gen":
        mat_a = random_matrix(args.n, args.seed)
        mat_b = random_matrix(args.n, args.seed + 1)

        export_blocks(mat_a, "A", args.block_size, args.out_a)
        export_blocks(mat_b, "B", args.block_size, args.out_b)

        total_blocks = math.ceil(args.n / args.block_size)
        print(f"Block files written (num_blocks={total_blocks})")

    else:
        blocks = load_blocks(args.c_blocks, args.block_size)
        matrix_c = assemble_matrix(blocks, args.n, args.block_size)

        print("Matrix C reconstructed. Top-left 5x5:")
        limit = min(5, args.n)
        for i in range(limit):
            row = " ".join(f"{matrix_c[i][j]:.2f}" for j in range(limit))
            print(row)


if __name__ == "__main__":
    main()

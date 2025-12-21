#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from typing import Iterable, List, Tuple, Dict


def read_block(line: str) -> Tuple[str, int, int, List[float]]:
    fields = next(csv.reader([line]))
    matrix_id = fields[0].strip()
    row_idx = int(fields[1])
    col_idx = int(fields[2])
    values = list(map(float, fields[3:]))
    return matrix_id, row_idx, col_idx, values


def accumulate_product(result: List[float],
                       left: List[float],
                       right: List[float],
                       block_size: int) -> None:
    for i in range(block_size):
        row_offset = i * block_size
        for k in range(block_size):
            coeff = left[row_offset + k]
            if coeff == 0.0:
                continue
            col_offset = k * block_size
            for j in range(block_size):
                result[row_offset + j] += coeff * right[col_offset + j]


def generate_pairs(line: str,
                   block_size: int,
                   num_blocks: int
                   ) -> Iterable[Tuple[str, Tuple[str, int, List[float]]]]:
    if not line.strip():
        return []

    tag, x, y, data = read_block(line)

    expected = block_size * block_size
    if len(data) != expected:
        raise ValueError(f"Expected {expected} values per block, got {len(data)}")

    emitted = []

    if tag == "A":
        row_block, shared_block = x, y
        for col_block in range(num_blocks):
            emitted.append(
                (f"{row_block},{col_block}", ("A", shared_block, data))
            )

    elif tag == "B":
        shared_block, col_block = x, y
        for row_block in range(num_blocks):
            emitted.append(
                (f"{row_block},{col_block}", ("B", shared_block, data))
            )

    return emitted


def reduce_key(key: str,
               records: List[Tuple[str, int, List[float]]],
               block_size: int) -> str:
    left_map: Dict[int, List[float]] = {}
    right_map: Dict[int, List[float]] = {}

    for source, idx, block in records:
        if source == "A":
            left_map[idx] = block
        else:
            right_map[idx] = block

    result_block = [0.0] * (block_size * block_size)

    for k in left_map.keys() & right_map.keys():
        accumulate_product(
            result_block,
            left_map[k],
            right_map[k],
            block_size
        )

    row_block, col_block = key.split(",")
    formatted = [f"{v:.10g}" for v in result_block]
    return ",".join(["C", row_block, col_block] + formatted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block-size", type=int, default=64)
    parser.add_argument("--num-blocks", type=int, required=True)
    parser.add_argument("--out", default="C_blocks.csv")
    parser.add_argument("inputs", nargs="+", help="Input CSV block files")
    args = parser.parse_args()

    grouped_blocks = defaultdict(list)

    for filename in args.inputs:
        with open(filename, newline="") as file:
            for line in file:
                for key, value in generate_pairs(
                    line, args.block_size, args.num_blocks
                ):
                    grouped_blocks[key].append(value)

    with open(args.out, "w", newline="") as output:
        for key in sorted(grouped_blocks):
            output.write(
                reduce_key(key, grouped_blocks[key], args.block_size) + "\n"
            )

    print(f"Output written to {args.out} ({len(grouped_blocks)} blocks)")


if __name__ == "__main__":
    main()

'''
Test script to generate a CSV file validating mask generation for all unique
3-channel combinations from channels 0 to 31.
'''

import csv
from itertools import combinations
from controller import Controller

def run_full_mask_test_csv(csv_path="mask_validation_log.csv"):
    """
    Generate all unique 3-channel combinations from 0–31.
    Write each combination and its expected mask (binary + hex) to a CSV.
    """
    total = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ch1", "ch2", "ch3", "mask_binary", "mask_hex"])

        for combo in combinations(range(32), 3):
            ch = Controller.Channel(ids=list(combo), hold_time_ms=100)
            mask = ch.mask
            writer.writerow([
                combo[0],
                combo[1],
                combo[2],
                format(mask, "032b"),
                f"0x{mask:08X}",
            ])
            total += 1

    print(f"Mask validation complete. {total} combinations saved to {csv_path}")

if __name__ == "__main__":
    run_full_mask_test_csv()
    print("Done")
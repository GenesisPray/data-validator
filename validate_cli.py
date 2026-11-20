#!/usr/bin/env python3
"""
CLI Data Validator for Inventory Balance Checks.
Usage:
    python validate_cli.py [input_file.csv] [-o output_flagged.csv] [--type PHC|HC] [--facility NAME]
"""

import argparse
import sys
import os
from validator import validate_csv_content, generate_flagged_csv_bytes

def main():
    parser = argparse.ArgumentParser(
        description="Check inventory CSV for Beginning Balance + Received - Dispensed - Losses Adjustment balance and save flagged.csv"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="sample_inventory_data.csv",
        help="Path to input inventory CSV file (default: sample_inventory_data.csv)"
    )
    parser.add_argument(
        "-o", "--output",
        default="flagged.csv",
        help="Path to output flagged CSV file (default: flagged.csv)"
    )
    parser.add_argument(
        "--type",
        choices=["PHC", "HC", "ALL"],
        default="ALL",
        help="Filter rows by facility classification (PHC or HC)"
    )
    parser.add_argument(
        "--facility",
        default=None,
        help="Filter by specific facility name (exact or substring match)"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.001,
        help="Mathematical balance tolerance (default: 0.001)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    print(f"Reading input file: {args.input}...")
    with open(args.input, "r", encoding="utf-8-sig", errors="replace") as f:
        csv_text = f.read()

    result = validate_csv_content(csv_text, tolerance=args.tolerance)

    flagged_rows = result['flagged_rows']

    # Apply filters if requested
    if args.type != "ALL":
        target_type = args.type.upper()
        flagged_rows = [r for r in flagged_rows if r.get('facility_type', '').upper() == target_type]

    if args.facility:
        target_fac = args.facility.lower()
        flagged_rows = [r for r in flagged_rows if target_fac in r.get('facility', '').lower()]

    print("\n" + "="*60)
    print(" INVENTORY BALANCE AUDIT SUMMARY")
    print("="*60)
    print(f" Total records analyzed:      {result['total_rows']}")
    print(f" Total balanced rows:         {result['balanced_rows']}")
    print(f" Total flagged imbalanced:    {result['flagged_rows_count']}")
    if result['total_rows'] > 0:
        pct = (result['flagged_rows_count'] / result['total_rows']) * 100
        print(f" Discrepancy rate:            {pct:.1f}%")
    print(f" Unique facilities found:     {len(result['facilities'])}")
    print(f" Facility types present:      {', '.join(result['facility_types'])}")
    print("="*60)

    # Save flagged.csv
    flagged_bytes = generate_flagged_csv_bytes(flagged_rows, result['headers'])
    with open(args.output, "wb") as f:
        f.write(flagged_bytes)

    print(f"\n[SUCCESS] Flagged rows saved to: '{args.output}' ({len(flagged_rows)} rows)")

    # Print first few flagged rows preview
    if flagged_rows:
        print("\nPreview of Flagged Discrepancies (first 5):")
        print("-" * 100)
        print(f"{'Row':<5} | {'Facility':<20} | {'Type':<5} | {'Commodity':<30} | {'Calc EB':<8} | {'Rep EB':<8} | {'Variance':<8}")
        print("-" * 100)
        for r in flagged_rows[:5]:
            calc_eb = r.get('calculated_ending_balance')
            rep_eb = r.get('reported_ending_balance')
            disc = r.get('discrepancy')
            print(f"{r['row_num']:<5} | {r['facility'][:20]:<20} | {r['facility_type']:<5} | {r['commodity'][:30]:<30} | {str(calc_eb):<8} | {str(rep_eb):<8} | {str(disc):<8}")
        print("-" * 100)

if __name__ == "__main__":
    main()


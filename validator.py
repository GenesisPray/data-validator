"""
Data Validator Engine for Health Logistics CSVs
Validates inventory balance: Beginning Balance + Received - Dispensed - Losses Adjustment == Ending Balance
"""

import csv
import io
import re
from typing import Dict, List, Any, Optional, Tuple

COLUMN_ALIASES = {
    'facility': [
        'facility', 'facility_name', 'facility name', 'health_facility', 'health facility',
        'site', 'site_name', 'location', 'centre', 'center', 'clinic'
    ],
    'facility_type': [
        'facility_type', 'facility type', 'type', 'classification', 'facility_classification',
        'facility classification', 'level', 'tier'
    ],
    'commodity': [
        'commodity', 'commodity_name', 'commodity name', 'product', 'product_name',
        'product name', 'item', 'item_name', 'item name', 'drug', 'medicine', 'description'
    ],
    'beginning_balance': [
        'beginning balance', 'beginning_balance', 'beg balance', 'beg_balance',
        'opening balance', 'opening_balance', 'start balance', 'start_balance',
        'initial balance', 'initial_balance', 'bb', 'ob'
    ],
    'received': [
        'received', 'quantity received', 'quantity_received', 'qty received', 'qty_received',
        'receipts', 'stock received', 'stock_received', 'rec'
    ],
    'dispensed': [
        'dispensed', 'quantity dispensed', 'quantity_dispensed', 'qty dispensed', 'qty_dispensed',
        'consumption', 'consumed', 'issued', 'quantity issued', 'qty issued', 'disp'
    ],
    'losses_adjustment': [
        'losses adjustment', 'losses_adjustment', 'loss adjustment', 'loss_adjustment',
        'losses and adjustments', 'losses_and_adjustments', 'losses / adjustments',
        'losses / adjustment', 'losses/adjustments', 'loss/adj', 'losses', 'loss',
        'adjustments', 'adjustment', 'adj'
    ],
    'ending_balance': [
        'ending balance', 'ending_balance', 'end balance', 'end_balance',
        'closing balance', 'closing_balance', 'physical count', 'physical_count',
        'physical stock', 'physical_stock', 'counted balance', 'counted_balance',
        'eb', 'cb'
    ]
}


def normalize_col_name(col: str) -> str:
    """Normalize column header for alias matching."""
    if not col:
        return ''
    s = col.strip().lower()
    # Replace separators with single space or underscore
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
    return s


def map_columns(headers: List[str]) -> Dict[str, Optional[str]]:
    """
    Map input CSV headers to standard internal field names.
    Returns dict: standard_name -> actual_header_name
    """
    mapping = {k: None for k in COLUMN_ALIASES.keys()}
    normalized_headers = {h: normalize_col_name(h) for h in headers}

    for standard_name, aliases in COLUMN_ALIASES.items():
        # Check exact matches first
        for h, norm_h in normalized_headers.items():
            if norm_h in aliases:
                mapping[standard_name] = h
                break
        
        # If not matched, check substring matches
        if mapping[standard_name] is None:
            for h, norm_h in normalized_headers.items():
                for alias in aliases:
                    if alias in norm_h or norm_h in alias:
                        # Avoid colliding facility and facility_type
                        if standard_name == 'facility' and 'type' in norm_h:
                            continue
                        mapping[standard_name] = h
                        break
                if mapping[standard_name] is not None:
                    break

    return mapping


def infer_facility_type(facility_name: str, explicit_type: Optional[str] = None) -> str:
    """
    Classify facility as PHC or HC.
    PHC = Primary Health Centre
    HC = Health Centre / Hospital / Clinic
    """
    if explicit_type:
        val = str(explicit_type).strip().upper()
        if 'PHC' in val or 'PRIMARY' in val:
            return 'PHC'
        if 'HC' in val or 'HEALTH CENTRE' in val or 'HEALTH CENTER' in val or 'HOSPITAL' in val or 'CLINIC' in val:
            return 'HC'
        return val

    # Infer from facility name
    name_upper = (facility_name or '').upper()
    if 'PHC' in name_upper or 'PRIMARY' in name_upper:
        return 'PHC'
    if 'HC' in name_upper or 'HEALTH CENTRE' in name_upper or 'CENTER' in name_upper or 'CLINIC' in name_upper or 'HOSPITAL' in name_upper:
        return 'HC'
    
    # Default to PHC if ambiguous in primary healthcare context, or HC
    return 'PHC'


def parse_numeric(val: Any) -> Tuple[Optional[float], Optional[str]]:
    """
    Safely parse numeric value from CSV cell.
    Handles commas, currency signs, blank, etc.
    Returns (float_value, error_message).
    """
    if val is None:
        return 0.0, None
    s = str(val).strip()
    if s == '' or s.lower() in ('na', 'n/a', 'null', 'none', '-'):
        return 0.0, None
    
    # Remove commas, dollar or other currency symbols, spaces
    s_cleaned = re.sub(r'[,\s$£€]', '', s)
    try:
        f = float(s_cleaned)
        # If integer equivalent, return clean round float
        return f, None
    except ValueError:
        return None, f"Non-numeric value: '{s}'"


def validate_csv_content(
    csv_text: str,
    tolerance: float = 0.001,
    facility_filter: Optional[str] = None,
    facility_type_filter: Optional[str] = None,
    custom_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Process CSV content and perform full balance checks.
    """
    # Detect dialect / delimiter
    csv_text_cleaned = csv_text.lstrip('\ufeff')  # strip BOM if present
    sample = csv_text_cleaned[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ','

    reader = csv.DictReader(io.StringIO(csv_text_cleaned), delimiter=delimiter)
    headers = reader.fieldnames or []
    
    mapping = map_columns(headers)
    if custom_mapping:
        for k, v in custom_mapping.items():
            if v in headers:
                mapping[k] = v

    total_rows = 0
    balanced_rows = 0
    flagged_rows: List[Dict[str, Any]] = []
    facilities_set = set()
    facility_types_found = set()
    facility_stats: Dict[str, Dict[str, Any]] = {}

    for idx, row in enumerate(reader, start=1):
        total_rows += 1
        
        raw_facility = row.get(mapping.get('facility') or '', '').strip() if mapping.get('facility') else f"Facility {idx}"
        raw_type = row.get(mapping.get('facility_type') or '', '').strip() if mapping.get('facility_type') else None
        commodity = row.get(mapping.get('commodity') or '', '').strip() if mapping.get('commodity') else 'General Commodity'

        fac_type = infer_facility_type(raw_facility, raw_type)
        facilities_set.add(raw_facility)
        facility_types_found.add(fac_type)

        if raw_facility not in facility_stats:
            facility_stats[raw_facility] = {
                'name': raw_facility,
                'type': fac_type,
                'total_rows': 0,
                'flagged_rows': 0,
                'balanced_rows': 0
            }
        facility_stats[raw_facility]['total_rows'] += 1

        # Check values
        bb_raw = row.get(mapping.get('beginning_balance') or '', '')
        rec_raw = row.get(mapping.get('received') or '', '')
        disp_raw = row.get(mapping.get('dispensed') or '', '')
        loss_raw = row.get(mapping.get('losses_adjustment') or '', '')
        eb_raw = row.get(mapping.get('ending_balance') or '', '') if mapping.get('ending_balance') else None

        bb_val, bb_err = parse_numeric(bb_raw)
        rec_val, rec_err = parse_numeric(rec_raw)
        disp_val, disp_err = parse_numeric(disp_raw)
        loss_val, loss_err = parse_numeric(loss_raw)
        
        has_eb = (mapping.get('ending_balance') is not None and eb_raw is not None and eb_raw.strip() != '')
        eb_val, eb_err = parse_numeric(eb_raw) if has_eb else (None, None)

        is_flagged = False
        flag_reasons: List[str] = []
        calculated_eb = 0.0
        discrepancy = 0.0

        # Check for numeric parsing errors
        parse_errors = [e for e in [bb_err, rec_err, disp_err, loss_err, eb_err] if e]
        if parse_errors:
            is_flagged = True
            flag_reasons.extend(parse_errors)
        else:
            # Check negative inputs where unexpected
            if bb_val < 0:
                is_flagged = True
                flag_reasons.append(f"Negative Beginning Balance ({bb_val})")
            if rec_val < 0:
                is_flagged = True
                flag_reasons.append(f"Negative Received Quantity ({rec_val})")
            if disp_val < 0:
                is_flagged = True
                flag_reasons.append(f"Negative Dispensed Quantity ({disp_val})")

            # Standard formula: Calculated Ending = Beginning + Received - Dispensed - Losses/Adjustment
            calculated_eb = (bb_val or 0.0) + (rec_val or 0.0) - (disp_val or 0.0) - (loss_val or 0.0)

            # Check if stock goes negative
            if calculated_eb < -tolerance:
                is_flagged = True
                deficit = abs(calculated_eb)
                flag_reasons.append(f"Negative Stock: Dispensed + Losses ({disp_val + loss_val}) exceed Available ({bb_val + rec_val}) by {deficit:.2f}")

            # Check against reported Ending Balance if present
            if has_eb and eb_val is not None:
                diff = eb_val - calculated_eb
                if abs(diff) > tolerance:
                    is_flagged = True
                    discrepancy = diff
                    if diff > 0:
                        flag_reasons.append(f"Surplus Discrepancy: Reported EB ({eb_val}) > Calculated EB ({calculated_eb:.2f}) by +{diff:.2f}")
                    else:
                        flag_reasons.append(f"Deficit Discrepancy: Reported EB ({eb_val}) < Calculated EB ({calculated_eb:.2f}) by {diff:.2f}")
            elif not has_eb and not is_flagged:
                # If no ending balance column was provided, but calculated balance is ok,
                # we record calculated balance
                discrepancy = 0.0

        # Create row record
        row_record = {
            'row_num': idx,
            'facility': raw_facility,
            'facility_type': fac_type,
            'commodity': commodity,
            'beginning_balance': bb_val if bb_val is not None else bb_raw,
            'received': rec_val if rec_val is not None else rec_raw,
            'dispensed': disp_val if disp_val is not None else disp_raw,
            'losses_adjustment': loss_val if loss_val is not None else loss_raw,
            'reported_ending_balance': eb_val if (has_eb and eb_val is not None) else (eb_raw if has_eb else 'N/A'),
            'calculated_ending_balance': round(calculated_eb, 2),
            'discrepancy': round(discrepancy, 2),
            'is_flagged': is_flagged,
            'flag_reasons': flag_reasons,
            'flag_reason_str': '; '.join(flag_reasons) if flag_reasons else 'Balanced',
            'raw_row': row
        }

        if is_flagged:
            flagged_rows.append(row_record)
            facility_stats[raw_facility]['flagged_rows'] += 1
        else:
            balanced_rows += 1
            facility_stats[raw_facility]['balanced_rows'] += 1

    return {
        'total_rows': total_rows,
        'balanced_rows': balanced_rows,
        'flagged_rows_count': len(flagged_rows),
        'flagged_rows': flagged_rows,
        'facilities': sorted(list(facilities_set)),
        'facility_types': sorted(list(facility_types_found)),
        'facility_stats': list(facility_stats.values()),
        'headers': headers,
        'column_mapping': mapping,
        'delimiter': delimiter
    }


def generate_flagged_csv_bytes(flagged_rows: List[Dict[str, Any]], original_headers: List[str]) -> bytes:
    """
    Generate flagged.csv content including original columns and diagnostic fields.
    """
    output = io.StringIO()
    # Diagnostic columns to prepend or append
    extra_headers = [
        'Flag_Status',
        'Flag_Reason',
        'Facility_Classification',
        'Calculated_Ending_Balance',
        'Reported_Ending_Balance',
        'Discrepancy'
    ]
    
    # We will output diagnostic columns first, then all original columns
    fieldnames = extra_headers + [h for h in original_headers if h not in extra_headers]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    for item in flagged_rows:
        out_row = dict(item.get('raw_row', {}))
        out_row['Flag_Status'] = 'FLAGGED'
        out_row['Flag_Reason'] = item.get('flag_reason_str', '')
        out_row['Facility_Classification'] = item.get('facility_type', '')
        out_row['Calculated_Ending_Balance'] = item.get('calculated_ending_balance', '')
        out_row['Reported_Ending_Balance'] = item.get('reported_ending_balance', '')
        out_row['Discrepancy'] = item.get('discrepancy', '')
        writer.writerow(out_row)

    return output.getvalue().encode('utf-8-sig')


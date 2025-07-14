import os
import re
import statistics
import json
from datetime import datetime
from PyPDF2 import PdfReader

print("Current working directory:", os.getcwd())

folder_path = r'C:\Users\Tobias.Lippuner\OneDrive - MAF International\General\Documents\fuel_project\fuel_prices'

# Regex to extract date patterns: MM/YYYY, Month YYYY, or YYYY alone
pattern_date = re.compile(
    r'(\b\d{2}/\d{4}\b|'          # e.g. 04/2025
    r'\b[A-Z]{3,9} \d{4}\b|'      # e.g. AVRIL 2025 or APRIL 2025
    r'\b\d{4}\b)',                # e.g. 2024
    re.IGNORECASE
)

metrics = [
    'Domestic_MGA/L', 'Domestic_USD/L', 'Domestic_EUR/L',
    'International_MGA/L', 'International_USD/L', 'International_EUR/L'
]

# Month mapping covering English and French abbreviations and full names
MONTH_MAP = {
    # English abbreviations
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
    # English full names
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6,
    'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12,
    # French abbreviations and full names
    'JANVIER': 1, 'FEV': 2, 'FEVRIER': 2, 'MARS': 3, 'AVR': 4, 'AVRIL': 4, 'MAI': 5, 'JUIN': 6,
    'JUILLET': 7, 'AOUT': 8, 'AOÛT': 8, 'SEPTEMBRE': 9, 'OCTOBRE': 10, 'NOVEMBRE': 11, 'DECEMBRE': 12,
}

def parse_date_string(date_str):
    """
    Parse a date string (e.g., "AVRIL 2025", "04/2025", "2024") into a datetime object.
    Returns datetime(year, month, 1) for consistent sorting.
    """
    date_str_upper = date_str.upper().strip()
    # Debug print
    # print(f"Parsing date string: '{date_str_upper}'")

    # Try MM/YYYY format
    if re.match(r'^\d{2}/\d{4}$', date_str_upper):
        try:
            return datetime.strptime(date_str_upper, '%m/%Y')
        except ValueError:
            pass

    # Try to find month name and year
    # Extract year
    year_match = re.search(r'\b(\d{4})\b', date_str_upper)
    year = int(year_match.group(1)) if year_match else None

    # Try to find month in MONTH_MAP keys
    for month_name, month_num in MONTH_MAP.items():
        if month_name in date_str_upper:
            if year:
                return datetime(year, month_num, 1)
            else:
                # If no year found, default to January of year 1 (very early)
                return datetime.min

    # If only year is present (e.g., "2024")
    if year and len(date_str_upper) == 4:
        return datetime(year, 1, 1)

    # Fallback: unparseable dates get datetime.min to sort first
    return datetime.min

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
    return text

def normalize_number(num_str):
    # Remove spaces and dots used as thousands separators
    num_str = num_str.replace(' ', '').replace('.', '')
    # Replace comma with dot for decimal
    num_str = num_str.replace(',', '.')
    return float(num_str)

def parse_pdf_text(text):
    """
    Extract date and average metrics from PDF text.
    Returns (date_str, averages) or (date_str, None) if no data.
    """
    # Normalize text for date extraction
    text_upper = text.upper()
    date_match = pattern_date.search(text_upper)
    date_str = date_match.group(0).strip() if date_match else 'Unknown'

    airport_data = []
    lines = text.splitlines()

    for line in lines:
        # Extract decimal numbers (e.g., 123.45)
        numbers = re.findall(r'\d{1,3}(?:[ .]\d{3})*(?:[.,]\d+)', line)
        if len(numbers) >= 6:
            try:
                row_values = [normalize_number(num) for num in numbers[:6]]
                airport_data.append(row_values)
            except ValueError:
                continue

    if not airport_data:
        return date_str, None

    # Compute average per metric
    num_metrics = 6
    averages = []
    for idx in range(num_metrics):
        metric_values = [row[idx] for row in airport_data]
        if metric_values:
            averages.append(statistics.mean(metric_values))

    if len(averages) != num_metrics:
        return date_str, None

    return date_str, averages

def main():
    data_by_date = {}

    header = ['Year_Month'] + metrics
    print('--- Per-File Averages ---')
    print('\t'.join(header))

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(file_path)
            date_str, values = parse_pdf_text(text)

            print(f"File: {filename}, Extracted Date: {date_str}, Values Found: {'Yes' if values else 'No'}")

            if values:
                data_by_date.setdefault(date_str, []).append(values)

                averages_rounded = [round(v, 3) for v in values]
                row = [date_str] + [str(avg) for avg in averages_rounded]
                print('\t'.join(row))

    print('\n--- Overall Averages per Date (Sorted) ---')
    print('\t'.join(header))

    sorted_dates = sorted(data_by_date.keys(), key=parse_date_string)

    for date_str in sorted_dates:
        all_values = data_by_date[date_str]
        transposed = list(zip(*all_values))
        overall_averages = [round(statistics.mean(vals), 3) for vals in transposed]
        row = [date_str] + [str(avg) for avg in overall_averages]
        print('\t'.join(row))

    # Save to JSON
    output_json_path = 'fuel_price_averages.json'
    json_output_data = {}
    for date_str in sorted_dates:
        all_values = data_by_date[date_str]
        transposed = list(zip(*all_values))
        overall_averages = [round(statistics.mean(vals), 3) for vals in transposed]
        json_output_data[date_str] = overall_averages

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output_data, f, indent=4)

    print(f'\nData saved to {output_json_path}')

if __name__ == '__main__':
    main()

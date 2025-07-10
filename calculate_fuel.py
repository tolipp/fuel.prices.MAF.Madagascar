
import os
import re
import statistics
import json
from datetime import datetime # Import datetime for proper date parsing and sorting
from PyPDF2 import PdfReader

print("Current working directory:", os.getcwd())

folder_path = r'C:\Users\Tobias.Lippuner\OneDrive - MAF International\General\Documents\fuel_project\fuel_prices'

# Regex to extract year and month (e.g., "AVRIL 2025" or "04/2025")
# The regex itself seems fine for capturing these patterns.
pattern_date = re.compile(r'(\b\d{2}/\d{4}\b|\b[A-Z]{3,9} \d{4}\b|\b\d{4}\b)', re.IGNORECASE)

metrics = [
    'Domestic_MGA/L', 'Domestic_USD/L', 'Domestic_EUR/L',
    'International_MGA/L', 'International_USD/L', 'International_EUR/L'
]

# Mapping for month names to numbers
MONTH_MAP = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
    'JANVIER': 1, 'FEVRIER': 2, 'MARS': 3, 'AVRIL': 4, 'MAI': 5, 'JUIN': 6,
    'JUILLET': 7, 'AOUT': 8, 'SEPTEMBRE': 9, 'OCTOBRE': 10, 'NOVEMBRE': 11, 'DECEMBRE': 12
}

def parse_date_string(date_str):
    """
    Parses a date string (e.g., "AVRIL 2025", "04/2025", "2024") into a datetime object.
    Returns datetime(year, month, 1) for consistent sorting.
    """
    date_str_upper = date_str.upper()
    
    # Format: MM/YYYY (e.g., 04/2025)
    if re.match(r'\d{2}/\d{4}', date_str_upper):
        try:
            return datetime.strptime(date_str_upper, '%m/%Y')
        except ValueError:
            pass # Fall through to other formats
            
    # Format: MMM YYYY (e.g., AVRIL 2025)
    # Note: Regex captures 3-9 letter month names, so need to handle full names if possible.
    # For simplicity, we assume we extract a 3-letter abbreviation for the map lookup
    # or handle the full name in a more robust way.
    # If the pattern_date extracts 'AVRIL', we need to map 'AVR'
    for month_name, month_num in MONTH_MAP.items():
        if month_name in date_str_upper: # Check if month name is part of the string
            year_match = re.search(r'\d{4}', date_str_upper)
            if year_match:
                year = int(year_match.group(0))
                return datetime(year, month_num, 1)
                
    # Format: YYYY (e.g., 2024) - Assume January for sorting
    if re.match(r'\d{4}', date_str_upper) and len(date_str_upper) == 4:
        try:
            year = int(date_str_upper)
            return datetime(year, 1, 1)
        except ValueError:
            pass

    # Fallback for unknown or unparseable formats
    return datetime.min # Return a very early date so unparseable dates sort to the beginning

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
    return text

def parse_pdf_text(text):
    date_match = pattern_date.search(text)
    date_str = date_match.group(0).strip() if date_match else 'Unknown'

    # Extract all airport data rows
    airport_data = []
    lines = text.splitlines()
    
    for line in lines:
        # Look for lines that contain airport names and 6 price values
        # Each data line should have 6 decimal numbers (3 domestic + 3 international)
        numbers = re.findall(r'\b\d+\.\d+\b', line)
        
        # Skip header lines and other non-data lines
        if len(numbers) >= 6:
            # Take the first 6 numbers as the 6 metrics
            try:
                row_values = [float(num) for num in numbers[:6]]
                airport_data.append(row_values)
            except ValueError:
                continue
    
    if not airport_data:
        return date_str, None
    
    # Calculate averages across all airports for each metric
    num_metrics = 6
    averages = []
    
    for metric_idx in range(num_metrics):
        metric_values = [row[metric_idx] for row in airport_data]
        if metric_values:
            avg = statistics.mean(metric_values)
            averages.append(avg)
    
    if len(averages) != 6:
        return date_str, None
        
    return date_str, averages

# Dictionary to store all per-file averages grouped by date
data_by_date = {}

# Print header for per-file output
header = ['Year_Month'] + metrics
print('--- Per-File Averages ---')
print('\t'.join(header))

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)
        text = extract_text_from_pdf(file_path)
        date_str, values = parse_pdf_text(text)
        if values:
            # Store the values (per file) in the data structure
            if date_str not in data_by_date:
                data_by_date[date_str] = []
            data_by_date[date_str].append(values)

            # Print the per-file averages immediately
            averages_rounded = [round(v, 3) for v in values]
            row = [date_str] + [str(avg) for avg in averages_rounded]
            print('\t'.join(row))

# After processing all files, compute and print overall averages per date
print('\n--- Overall Averages per Date (Sorted) ---')
print('\t'.join(header))

# Sort the keys (date strings) using the custom parsing function
# to ensure sorting by year, then month
sorted_dates = sorted(data_by_date.keys(), key=parse_date_string)

for date_str in sorted_dates:
    all_values = data_by_date[date_str]  # list of lists (e.g., [[val1, val2,...], [val1, val2,...]])
    
    # Transpose to get lists of values per metric for averaging across files for this date
    # Example: if all_values = [[1,2,3], [4,5,6]]
    # then transposed = [(1,4), (2,5), (3,6)]
    transposed = list(zip(*all_values))
    
    overall_averages = [round(statistics.mean(vals), 3) for vals in transposed]
    row = [date_str] + [str(avg) for avg in overall_averages]
    print('\t'.join(row))

# Optional: Save the data structure to a JSON file for persistence
output_json_path = 'fuel_price_averages.json'
with open(output_json_path, 'w', encoding='utf-8') as f:
    # Prepare data for JSON: overall averages per date
    json_output_data = {}
    for date_str in sorted_dates:
        all_values = data_by_date[date_str]
        transposed = list(zip(*all_values))
        overall_averages = [round(statistics.mean(vals), 3) for vals in transposed]
        json_output_data[date_str] = overall_averages

    json.dump(json_output_data, f, indent=4)

print(f'\nData saved to {output_json_path}')
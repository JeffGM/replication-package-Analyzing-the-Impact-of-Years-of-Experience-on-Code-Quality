import csv

def replace_names(input_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=';')
        rows = list(reader)
        header = rows[0]
        
        # Process each row
        for index, row in enumerate(rows[1:], start=1):
            # Replace the name with "Dev {index}"
            row[2] = f"Dev {index}"
    
    # Write back to same file
    with open(input_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(header)
        writer.writerows(rows[1:])

# Usage
replace_names('../workana_profiles.csv')
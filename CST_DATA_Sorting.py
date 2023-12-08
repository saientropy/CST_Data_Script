import pandas as pd
import re

def process_file(file_path):
    datasets = {}
    current_frequency = None
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('#'):
                if current_frequency and data:
                    datasets[current_frequency] = pd.DataFrame(data, columns=['Arc Length', 'Electric Field'])
                    data = []
                match = re.search(r'(\d+(\.\d+)?) GHz', line)
                if match:
                    current_frequency = float(match.group(1))
            else:
                parts = line.split('\t')
                if len(parts) == 2:
                    arc_length, electric_field = map(float, parts)
                    data.append((arc_length, electric_field))
        if current_frequency and data:
            datasets[current_frequency] = pd.DataFrame(data, columns=['Arc Length', 'Electric Field'])
    return datasets

def create_complex_dataset(real_datasets, imaginary_datasets):
    complex_datasets = {}
    for frequency in real_datasets.keys():
        real_df = real_datasets[frequency]
        imaginary_df = imaginary_datasets[frequency]
        complex_df = real_df.copy()
        complex_df['Electric Field'] = complex_df['Electric Field'] + 1j * imaginary_df['Electric Field']
        complex_datasets[frequency] = complex_df
    return complex_datasets

def subtract_datasets(datasets1, datasets2):
    results = {}
    for frequency in datasets1.keys():
        df1 = datasets1[frequency]
        df2 = datasets2[frequency]
        result_df = df1.copy()
        result_df['Electric Field'] = df1['Electric Field'] - df2['Electric Field']
        results[frequency] = result_df
    return results

# File names - replace these with your file names
e_tot_real_file_name = 'E_tot_real.txt'  # Replace with your file name
e_tot_imaginary_file_name = 'E_tot_imaginary.txt'  # Replace with your file name
e_incident_real_file_name = 'E_incident_real.txt'  # Replace with your file name
e_incident_imaginary_file_name = 'E_incident_imaginary.txt'  # Replace with your file name

# Process each file
datasets_e_tot_real = process_file(e_tot_real_file_name)
datasets_e_tot_imaginary = process_file(e_tot_imaginary_file_name)
datasets_e_incident_real = process_file(e_incident_real_file_name)
datasets_e_incident_imaginary = process_file(e_incident_imaginary_file_name)

# Create complex datasets
e_tot_complex = create_complex_dataset(datasets_e_tot_real, datasets_e_tot_imaginary)
e_incident_complex = create_complex_dataset(datasets_e_incident_real, datasets_e_incident_imaginary)

# Compute E_diff_complex
e_diff_complex = subtract_datasets(e_tot_complex, e_incident_complex)

# Function to save datasets to CSV files
def save_datasets(datasets, output_file_path):
    base_frequency = list(datasets.keys())[0]
    consolidated_df = datasets[base_frequency][['Arc Length']].copy()
    for frequency, df in datasets.items():
        consolidated_df[f'E_field_{frequency}GHz'] = df['Electric Field'].apply(str)
    consolidated_df.to_csv(output_file_path, index=False)

# Output file paths
e_tot_complex_path = 'E_tot_complex.csv'
e_incident_complex_path = 'E_incident_complex.csv'
e_diff_complex_path = 'E_diff_complex.csv'

# Saving the datasets to CSV files
save_datasets(e_tot_complex, e_tot_complex_path)
save_datasets(e_incident_complex, e_incident_complex_path)
save_datasets(e_diff_complex, e_diff_complex_path)

print("Files saved: E_tot_complex.csv, E_incident_complex.csv, E_diff_complex.csv")

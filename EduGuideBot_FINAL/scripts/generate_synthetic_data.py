# scripts/generate_synthetic_data.py
import pandas as pd
import numpy as np
import os

# --- Configuration ---
NUM_STUDENTS = 10000
OUTPUT_CSV_PATH = 'data/synthetic_admissions_data.csv'
MAJOR_CATEGORIES = [
    "ធុរកិច្ច", "វិស្វកម្ម", "បច្ចេកវិទ្យា", "ភាសា", "ច្បាប់", "ទេសចរណ៍",
    "កសិកម្ម", "ស្ថាបត្យកម្ម", "សេដ្ឋកិច្ច", "អប់រំ", "រដ្ឋបាល", "វេជ្ជសាស្ត្រ",
    "សុខភាព", "សិល្បៈ", "បុរាណវិទ្យា", "វិទ្យាសាស្ត្រ", "ព្រៃឈើ", "ជលផល",
    "បរិស្ថាន", "ទំនាក់ទំនងអន្តរជាតិ", "សារព័ត៌មាន"
]
UNIVERSITY_IDS = list(range(1, 49))

def label_admission_decision(row):
    # Rule 1: Top-Tier Tech (ITC, CADT)
    if row['applied_university_id'] in [10, 27] and row['applied_major_category'] in ['បច្ចេកវិទ្យា', 'វិស្វកម្ម']:
        return 1 if row['gpa'] >= 3.5 and row['english_proficiency'] >= 7 else 0
    # Rule 2: Top-Tier Medical (UP, IU)
    if row['applied_university_id'] in [14, 15] and row['applied_major_category'] in ['វេជ្ជសាស្ត្រ', 'សុខភាព']:
        return 1 if row['gpa'] >= 3.6 else 0
    # Rule 3: Top-Tier Business/Law (NUM, RULE)
    if row['applied_university_id'] in [16, 12] and row['applied_major_category'] in ['ធុរកិច្ច', 'ច្បាប់']:
        return 1 if row['gpa'] >= 3.2 else 0
    # Rule 4: Premium International (AUPP, Paragon)
    if row['applied_university_id'] in [28, 36]:
        return 1 if row['english_proficiency'] >= 8 and row['gpa'] >= 3.0 else 0
    # Default Rule
    admission_chance = row['gpa'] / 4.0 + row['extracurriculars'] * 0.05
    return 1 if np.random.rand() < admission_chance else 0

def generate_data():
    """Generates the main synthetic dataset."""
    print("--- Starting Synthetic Data Generation ---")
    
    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')

    gpas = np.random.normal(loc=3.2, scale=0.4, size=NUM_STUDENTS).round(2)
    gpas = np.clip(gpas, 2.0, 4.0)

    data = {
        'gpa': gpas,
        'english_proficiency': np.random.randint(1, 11, size=NUM_STUDENTS),
        'extracurriculars': np.random.randint(0, 6, size=NUM_STUDENTS),
        'applied_university_id': np.random.choice(UNIVERSITY_IDS, size=NUM_STUDENTS),
        'applied_major_category': np.random.choice(MAJOR_CATEGORIES, size=NUM_STUDENTS),
    }
    df = pd.DataFrame(data)
    df['admission_decision'] = df.apply(label_admission_decision, axis=1)
    
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"✅ Successfully generated and saved {len(df)} records to {OUTPUT_CSV_PATH}")
    
    print("\n--- Verification ---")
    decision_counts = df['admission_decision'].value_counts(normalize=True) * 100
    print("Admission Decision Distribution:")
    print(f"Admitted (1): {decision_counts.get(1, 0):.1f}%")
    print(f"Rejected (0): {decision_counts.get(0, 0):.1f}%")
    
if __name__ == '__main__':
    generate_data()
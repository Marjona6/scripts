import pandas as pd
import re
import os
from datetime import datetime
import json

def convert_date_format(date_str):
    # Check if the input is a string before attempting to convert
    if isinstance(date_str, str):
        # Try parsing with the first format '%d/%m/%Y'
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass  # If parsing with the first format fails, try the next format
        
        # Try parsing with the second format '%d-%m-%Y'
        try:
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return date_str  # Return the original string if both formats fail to parse
    return date_str  # Return the original input if it is not a string

def clean_number_column(value):
    # First pass: Remove anything after a dot (.) or inside parentheses ()
    value = re.sub(r'\..*|\(.*\)', '', str(value))
    
    # Second pass: Extract integers separated by spaces or commas
    numbers = re.findall(r'\b\d+\b', value)
    
    # Convert the extracted numbers to integers and return
    return [int(num) for num in numbers]

def clean_language_column(value):
    eu_languages = [
        'Bulgarian', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 
        'Finnish', 'French', 'German', 'Greek', 'Hungarian', 'Irish', 'Italian', 
        'Latvian', 'Lithuanian', 'Maltese', 'Polish', 'Portuguese', 'Romanian', 
        'Slovak', 'Slovenian', 'Spanish', 'Swedish'
    ]
    
    language_abbreviations = {
        'EN': 'English',
        'FR': 'French',
        'DE': 'German',
        'ES': 'Spanish',
        'IT': 'Italian',
        'PT': 'Portuguese',
        'NL': 'Dutch',
        'PL': 'Polish',
        'RO': 'Romanian',
        'HU': 'Hungarian',
        'CS': 'Czech',
        'BG': 'Bulgarian',
        'HR': 'Croatian',
        'DA': 'Danish',
        'FI': 'Finnish',
        'EL': 'Greek',
        'GA': 'Irish',
        'LT': 'Lithuanian',
        'LV': 'Latvian',
        'SK': 'Slovak',
        'SL': 'Slovenian',
        'SV': 'Swedish',
    }

    if isinstance(value, float):
        value = str(value)

    value = re.sub(r'\ball\s*eu\b', 'All_EU', value, flags=re.IGNORECASE)
    cleaned_value = re.sub(r'[^\w\s]', ' ', str(value))
    languages = [lang.strip() for lang in re.split(r'\s+and\s+|\s+', cleaned_value) if lang.strip()]

    result = []
    for lang in languages:
        if lang.lower() == 'all_eu':
            result.extend(eu_languages)
        else:
            lang = language_abbreviations.get(lang.upper(), lang)
            result.append(lang)
    
    result = [lang for lang in result if lang in language_abbreviations.values() or lang in eu_languages]

    # Format as a JSON array
    return json.dumps(result)

def main():
    input_file = 'input.csv'
    output_file = 'output.csv'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    
    # Drop rows where all non-boolean values are empty or False
    df = df.dropna(how='all', subset=df.columns[df.dtypes != bool].tolist()).reset_index(drop=True)

    if 'date_of_decision' in df.columns:
        df['date_of_decision'] = df['date_of_decision'].apply(convert_date_format)

    
    # Apply clean_language_column only to non-float values
    df['language_of_decision'] = df['language_of_decision'].apply(lambda x: clean_language_column(x) if not isinstance(x, float) else x)
    df['eu_fundamental_rights_charter_articles'] = df['eu_fundamental_rights_charter_articles'].apply(clean_number_column)

    df.to_csv(output_file, index=False)
    print(f"Data cleaned and saved to {output_file}")

if __name__ == "__main__":
    main()


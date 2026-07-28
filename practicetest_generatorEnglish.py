import json
import random
import requests

BASE_URL = "https://api.jsonsilo.com/public/942c3c3b-3a0c-4be3-81c2-12029def19f5"

def question_collecter(section, domain, num):
    """
    Collects 'num' random question indices from the specified 'section' and 'domain'
    using query parameters to filter by subject (?section=english or ?section=MATH).
    """
    # Force uppercase for MATH if API expects MATH, lower for english
    sec_param = "MATH" if section.lower() == "math" else "english"
    
    response = requests.get(BASE_URL, params={'section': sec_param})
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for section: {section}")
        return []

    data = response.json()
    
    # Extract list depending on API structure
    questions = data.get(section, []) if isinstance(data, dict) else data

    # Clean domain string to avoid mismatch on trailing spaces
    # Clean domain string to avoid mismatch on trailing spaces
    target_domain = domain.strip()
    collected_questions = [
          question for question in questions
          if question.get('domain', '').strip() == target_domain
    ]
  
    return random.sample(collected_questions, num) if len(collected_questions) >= num else collected_questions
  
def open_and_modify(file_path, path, new_value, append=False, create_if_missing=False):
    """Navigates through nested JSON paths to modify or append data."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    current = data
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                if create_if_missing:
                    current[key] = {} if isinstance(path[i + 1], str) else []
                else:
                    raise KeyError(f"Key '{key}' not found in dict.")
            current = current[key]
        elif isinstance(current, list):
            if isinstance(key, int) and 0 <= key < len(current):
                current = current[key]
            else:
                raise IndexError(f"Index '{key}' out of range.")

    last_key = path[-1]
    if isinstance(current, dict):
        if last_key in current:
            if isinstance(current[last_key], list) and append:
                current[last_key].extend(new_value)
            else:
                current[last_key] = new_value
        elif create_if_missing:
            current[last_key] = new_value if not append else [new_value]
        else:
            raise KeyError(f"Key '{last_key}' not found.")

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def create_empty_test(file_path, test_name, subject, num_modules=2):
    """Helper to initialize an empty test entry under the appropriate section."""
    top_key = f"{subject}_tests"  # 'english_tests' or 'math_tests'
    open_and_modify(file_path, [top_key], [], create_if_missing=True)

    new_test = {'name': test_name}
    for m in range(1, num_modules + 1):
        new_test[f'module_{m}'] = []

    open_and_modify(file_path, [top_key], [new_test], append=True)

    # Return the index of the newly added test
    with open(file_path, 'r') as f:
        data = json.load(f)
    return len(data[top_key]) - 1


# 1. ENGLISH ONLY TEST GENERATOR

def generate_english_test(file_path, test_name, num_questions=27):
    """Generates a standalone English test (2 modules)."""
    test_idx = create_empty_test(file_path, test_name, subject='english', num_modules=2)

    for module_num in [1, 2]:
        for i in range(1, num_questions + 1):
            if 1 <= i < 8:
                domain = 'Information and Ideas'
            elif 8 <= i < 15:
                domain = 'Craft and Structure'
            elif 15 <= i < 21:
                domain = 'Expression of Ideas'
            else:
                domain = 'Standard English Conventions'

            q_ids = question_collecter('english', domain, 1)
            open_and_modify(
                file_path,
                ['english_tests', test_idx, f'module_{module_num}'],
                q_ids,
                append=True
            )


# EXAMPLE USAGE

file_path = 'dataEnglish.json'

# Generate 4 English-only practice tests
for x in range(1, 5):
    generate_english_test(file_path, f'English Practice Test #{x}', num_questions=27)

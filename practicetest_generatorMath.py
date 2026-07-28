import json
import random
import requests

BASE_URL = "https://api.jsonsilo.com/public/942c3c3b-3a0c-4be3-81c2-12029def19f5"

def fetch_all_questions():
    """Fetches the dataset ONCE to avoid API rate limits (HTTP 429)."""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            data = response.json()
            # Handle dictionary vs list formats
            if isinstance(data, dict):
                for key, val in data.items():
                    if key.lower() == 'math':
                        return val
            return data if isinstance(data, list) else []
        else:
            print(f"API Error: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Network error: {e}")
        return []


def collect_math_questions(all_questions, domain, num):
    """Filters questions in memory without making extra API calls."""
    target_domain = domain.strip()
    collected = [
        q for q in all_questions
        if q.get('domain', '').strip() == target_domain
    ]
    if len(collected) >= num:
        return random.sample(collected, num)
    return collected


def generate_math_test(all_questions, test_name):
    """Builds a single Math test dictionary with 2 modules."""
    test_data = {
        'name': test_name,
        'module_1': [],
        'module_2': []
    }

    for module_num in [1, 2]:
        module_key = f'module_{module_num}'
        for i in range(1, 23):
            if 1 <= i < 8:
                domain = 'Algebra'
                count = 2
            elif 8 <= i < 15:
                domain = 'Advanced Math'
                count = 2
            elif 15 <= i < 21:
                domain = 'Problem-Solving and Data Analysis'
                count = 1
            else:
                domain = 'Geometry and Trigonometry'
                count = 1

            q_ids = collect_math_questions(all_questions, domain, count)
            test_data[module_key].extend(q_ids)

    return test_data


# RUN GENERATOR
if __name__ == "__main__":
    file_path = 'dataMath.json'

    print("Fetching math dataset...")
    math_pool = fetch_all_questions()

    if not math_pool:
        print("Failed to load questions. Make sure you aren't currently rate-limited by JSONSilo!")
    else:
        output_data = {'math_tests': []}
        for x in range(1, 5):
            print(f"Generating Math Practice Test #{x}...")
            test_obj = generate_math_test(math_pool, f'Math Practice Test #{x}')
            output_data['math_tests'].append(test_obj)

        # Save to file ONCE at the end
        with open(file_path, 'w') as f:
            json.dump(output_data, f, indent=4)

        print(f"Done! Successfully generated 4 tests in '{file_path}'.")
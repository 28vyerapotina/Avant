import json
import random

DATA_FILE = 'dataMath.json'

def load_data():
    """Reads the dataMath.json file safely."""
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: Could not read '{DATA_FILE}'. Make sure test data is generated first!")
        return {}


def practicetest_generatorMath(level_num=1, count=5):
    """
    Retrieves 'count' questions for Math combat from data.json.
    """
    data = load_data()
    math_tests = data.get('math_tests', [])

    if not math_tests:
        print("No Math tests found in data.json!")
        return []

    # Pick a test based on the level number
    test_index = (level_num - 1) % len(math_tests)
    target_test = math_tests[test_index]

    # Gather all questions from module_1 and module_2
    all_questions = []
    for key, value in target_test.items():
        if key.startswith('module_') and isinstance(value, list):
            all_questions.extend(value)

    if not all_questions:
        return []

    # Return random sample of questions
    return random.sample(all_questions, min(count, len(all_questions)))


if __name__ == "__main__":
    sample = practicetest_generatorMath(level_num=1, count=5)
    print(f"Loaded {len(sample)} Math questions.")
    
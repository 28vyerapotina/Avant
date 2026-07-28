import random
#this doest do anything yet, it just prints PS C:\Users\ajoke\OneDrive\Documents\GitHub\Avant> & C:\Users\ajoke\AppData\Local\Programs\Python\Python312\python.exe c:/Users/ajoke/OneDrive/Documents/GitHub/Avant/azure-rivals/sat_engine.py
QUESTION_BANK = {
    1:[
        {
            "prompt": "Choose the word that best completes the sentece:\n\nThe team was ________ by their surprising champions victory.",
            "options": [
                "A) Elated",
                "B) Dejected",
                "C) Reluctant",
                "D) Lethargic"
            ],
            "correct": 0,
            "topic": "Vocabulary",
        },
        {
            "prompt": "Identify the error:\n\nNeither of the answers were correct.",
            "options": [
                "A) Neither",
                "B) of the",
                "C) were",
                "D) No error"
            ],
            "correct": 2,
            "topic": "Grammar",
        },
    ],
    2: [  # Level 2: Easy Math
        {
            "prompt": "If 3x + 5 = 20, what is the value of x?",
            "options": ["A) 3", "B) 5", "C) 15", "D) 25"],
            "correct": 1,  # B is index 1
            "topic": "Algebra",
        }
    ],
}


class SATEngine:

    def __init__(self):
        self.current_level = 1
        self.total_correct = 0
        self.total_answered = 0

    def get_question(self):
        """Fetches a random question based on current level."""
        questions = QUESTION_BANK.get(self.current_level, QUESTION_BANK[1])
        return random.choice(questions)

    def check_answer(self, question, selected_index):
        """Checks if answer is right and tracks stats."""
        self.total_answered += 1
        is_correct = selected_index == question["correct"]
        if is_correct:
            self.total_correct += 1
        return is_correct
    
import json
import os
import random
import webbrowser

# 1. Load the real questions generated in your data.json
try:
    with open('data.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: data.json not found! Run your generator script first.")
    exit()

# 2. Gather all available questions from the generated tests
all_questions = []
for test in data.get('practice_test', []):
    for mod in ['module_1', 'module_2']:
        all_questions.extend(test.get(mod, []))

if len(all_questions) < 3:
    print("Error: You need at least 3 questions inside data.json to play. Generate more tests first!")
    exit()

# 3. Grab exactly 3 random questions for this combat encounter
combat_questions = random.sample(all_questions, 3)

# 4. Generate the fully interactive HTML page with JavaScript functionality
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Azure Rivals - Combat Encounter</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; 
            background: #0f172a; 
            color: #f1f5f9; 
            max-width: 750px; 
            margin: 40px auto; 
            padding: 0 20px;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #334155;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        .header h1 { color: #38bdf8; margin: 0; font-size: 2.2em; text-transform: uppercase; letter-spacing: 2px; }
        .header p { color: #94a3b8; margin: 5px 0 0 0; }
        .question-card { 
            background: #1e293b; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); 
            margin-bottom: 25px; 
            border: 1px solid #334155;
        }
        .tag { 
            font-size: 0.75em; 
            background: #0284c7; 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            color: white; 
            text-transform: uppercase;
        }
        .passage { background: #0f172a; padding: 15px; border-radius: 8px; border-left: 4px solid #38bdf8; margin: 15px 0; font-size: 0.95em; color: #cbd5e1; }
        .prompt { font-weight: bold; font-size: 1.05em; margin-bottom: 15px; color: #f8fafc; }
        .choice-container { display: flex; flex-direction: column; gap: 10px; }
        .choice { 
            padding: 12px 15px; 
            background: #334155; 
            border: 1px solid #475569; 
            border-radius: 6px; 
            cursor: pointer; 
            transition: all 0.2s ease;
            font-size: 0.95em;
        }
        .choice:hover { background: #475569; border-color: #64748b; }
        
        /* Interactive Response States */
        .choice.correct-clicked { background: #16a34a !important; border-color: #22c55e !important; color: white; font-weight: bold; }
        .choice.wrong-clicked { background: #dc2626 !important; border-color: #ef4444 !important; color: white; }
        .choice.revealed-correct { background: #15803d !important; border-color: #16a34a !important; color: white; opacity: 0.9; font-weight: bold;}
        .choice.disabled { pointer-events: none; }
        
        .footer-action { text-align: center; margin-top: 40px; margin-bottom: 60px; }
        .return-btn { 
            display: none; 
            background: #38bdf8; 
            color: #0f172a; 
            font-weight: bold; 
            font-size: 1.2em; 
            padding: 15px 40px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            text-transform: uppercase;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
        .return-btn:hover { background: #7dd3fc; }
    </style>
</head>
<body>

    <div class="header">
        <h1>⚔️ Azure Rivals Combat Encounter</h1>
        <p>Answer 3 questions correctly to unleash your attack!</p>
    </div>

    <div id="quiz-container">
"""

for idx, q in enumerate(combat_questions, 1):
    q_text = q.get('question', {})
    paragraph = q_text.get('paragraph', '')
    prompt = q_text.get('question', '')
    choices = q_text.get('choices', {})
    correct = q_text.get('correct_answer', '')

    html_content += f"""
    <div class="question-card" data-correct="{correct}">
        <span class="tag">{q.get('domain', 'SAT Question')}</span>
        {"<div class='passage'>" + paragraph + "</div>" if paragraph else ""}
        <p class="prompt"><strong>Q{idx}.</strong> {prompt}</p>
        <div class="choice-container">
    """
    for letter, choice_text in choices.items():
        html_content += f'<div class="choice" data-letter="{letter}"><strong>{letter})</strong> {choice_text}</div>'
    
    html_content += "</div></div>"

html_content += """
    </div>

    <div class="footer-action">
        <button class="return-btn" id="returnBtn" onclick="window.close()">⚡ Return to Fighting Arena</button>
    </div>

    <script>
        let answeredCount = 0;
        const totalQuestions = 3;

        document.querySelectorAll('.question-card').forEach(card => {
            const correctAnswer = card.getAttribute('data-correct');
            const choices = card.querySelectorAll('.choice');

            choices.forEach(choice => {
                choice.addEventListener('click', () => {
                    const selectedLetter = choice.getAttribute('data-letter');
                    
                    // Freeze all choices for this specific question card
                    choices.forEach(c => c.classList.add('disabled'));

                    if (selectedLetter === correctAnswer) {
                        choice.classList.add('correct-clicked');
                    } else {
                        choice.classList.add('wrong-clicked');
                        // Find and highlight the right choice anyway
                        card.querySelector(`[data-letter="${correctAnswer}"]`).classList.add('revealed-correct');
                    }

                    // Count this question as completed
                    answeredCount++;
                    if (answeredCount === totalQuestions) {
                        document.getElementById('returnBtn').style.display = 'inline-block';
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# Save out the combat encounter mockup
with open('combat_encounter.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

webbrowser.open('file://' + os.path.realpath('combat_encounter.html'))
print("Combat Encounter initialized! Answer 3 questions to unlock the return button.")

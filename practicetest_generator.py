import json
import os
import webbrowser

with open('data.json', 'r') as file:
    data = json.load(file)

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>SAT Practice Tests</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f8fafc; color: #1e293b; }
        h1 { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        .test-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 30px; border: 1px solid #e2e8f0; }
        .module-title { font-weight: bold; color: #2563eb; font-size: 1.1em; margin-top: 20px; background: #eff6ff; padding: 8px 12px; border-radius: 6px; }
        .question-box { background: #fdfdfd; border-left: 4px solid #cbd5e1; padding: 14px 16px; margin: 14px 0; border-radius: 0 8px 8px 0; }
        .choice { padding: 4px 0; padding-left: 10px; margin: 2px 0; border-radius: 4px; }
        .correct { color: #16a34a; font-weight: bold; background: #f0fdf4; }
        .tag { font-size: 0.75em; background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-weight: bold; color: #64748b; text-transform: uppercase; }
    </style>
</head>
<body>
    <h1>Generated SAT Practice Tests</h1>
"""

for test in data.get('practice_test', []):
    html_content += f'<div class="test-card"><h2>✨ {test.get("name", "Unnamed Test")}</h2>'

    for mod_name in ['module_1', 'module_2']:
        questions = test.get(mod_name, [])
        html_content += f'<div class="module-title">{mod_name.replace("_", " ").title()} ({len(questions)} Questions)</div>'

        for idx, q in enumerate(questions, 1):
            q_text = q.get('question', {})
            paragraph = q_text.get('paragraph', '')
            prompt = q_text.get('question', '')
            choices = q_text.get('choices', {})
            correct = q_text.get('correct_answer', '')

            html_content += f'<div class="question-box"><span class="tag">{q.get("domain","")}</span>'
            if paragraph:
                html_content += f'<p>{paragraph}</p>'
            html_content += f'<p><strong>Q{idx}.</strong> {prompt}</p>'
            
            for letter, choice_text in choices.items():
                style = 'correct' if letter == correct else ''
                html_content += f'<div class="choice {style}"><strong>{letter})</strong> {choice_text}</div>'
            html_content += '</div>'

    html_content += '</div>'

html_content += "</body></html>"

with open('viewer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

webbrowser.open('file://' + os.path.realpath('viewer.html'))
print("Successfully opened the visual test document in your web browser!")

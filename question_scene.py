import pygame
import sys
import pandas as pd

pygame.init()
import dataframe_training
# ---------------------------------------------------------------------------
# Expected DataFrame schema
# ---------------------------------------------------------------------------
# The DataFrame passed into run_question_scene should have these columns:
#
#   domain                      str   (optional - used to filter which rows to show)
#   difficulty                  any   (optional - used to filter which rows to show)
#   question.paragraph          str   (optional - a reading passage / context block)
#   question.question           str   (required - the prompt text)
#   question.choices.A          str   (required)
#   question.choices.B          str   (required)
#   question.choices.C          str   (optional)
#   question.choices.D          str   (optional)
#   question.correct_answer     str   (required - one of "A", "B", "C", "D")
#   question.explanation        str   (optional - shown after the question is answered)
#
# Missing question.choices.C / question.choices.D cells (NaN or empty string)
# are simply skipped, so this works for both 2-option and 4-option questions.
# These dotted names are typical of a DataFrame built from json_normalize()-ing
# nested question records, e.g. pd.json_normalize(records, sep=".").
# ---------------------------------------------------------------------------


def wrap_text(text, font, max_width):
    if not text:
        return []
    words = str(text).split(' ')
    lines = []
    current = ""
    for word in words:
        test = current + word + " "
        if font.size(test)[0] > max_width:
            if current:
                lines.append(current.strip())
            current = word + " "
        else:
            current = test
    if current:
        lines.append(current.strip())
    return lines


def _get(row, col, default=""):
    val = row.get(col, default)
    return default if pd.isna(val) else val


def _row_to_question(row):
    """Convert a DataFrame row into the internal question dict this scene uses."""
    choices = {}
    for letter in "ABCD":
        col = f"question.choices.{letter}"
        val = _get(row, col, "")
        if str(val).strip() != "":
            choices[letter] = str(val)

    return {
        "paragraph": str(_get(row, "question.paragraph", "")),
        "question": str(_get(row, "question.question", "")),
        "choices": choices,
        "correct_answer": str(_get(row, "question.correct_answer", "")).strip().upper(),
        "explanation": str(_get(row, "question.explanation", "")),
    }


def load_questions_from_df(df, domain=None, difficulty=None, count=5,
                            shuffle=True, random_state=None):
    """
    Filter/sample a DataFrame of questions and convert to a list of question dicts.

    df            : pandas.DataFrame following the schema documented above.
    domain        : if provided and df has a 'domain' column, only rows matching
                    this domain are used.
    difficulty    : if provided and df has a 'difficulty' column, only rows
                    matching this difficulty are used.
    count         : max number of questions to return.
    shuffle       : if True, sample randomly; if False, take the first `count`
                    rows in order.
    random_state  : optional seed for reproducible sampling.
    """
    working = df.copy()

    if domain is not None and "domain" in working.columns:
        working = working[working["domain"] == domain]

    if difficulty is not None and "difficulty" in working.columns:
        working = working[working["difficulty"] == difficulty]

    if working.empty:
        return []

    if shuffle:
        working = working.sample(
            n=min(count, len(working)), random_state=random_state
        )
    else:
        working = working.head(count)

    return [_row_to_question(row) for _, row in working.iterrows()]


def run_question_scene(screen, df, domain=None, difficulty=None, count=5,
                        title="PRACTICE QUESTIONS", shuffle=True, random_state=None):
    """
    Runs a question scene sourced from a pandas DataFrame.

    domain     : optional filter matching the 'domain' column.
    difficulty : optional filter matching the 'difficulty' column.

    Returns (correct_count, total_questions, if_right).
    """
    WIDTH, HEIGHT = screen.get_size()

    BG_COLOR = (15, 23, 42)
    TEXT_COLOR = (241, 245, 249)
    CHOICE_BG = (30, 41, 59)
    CORRECT_GREEN = (34, 197, 94)
    WRONG_RED = (220, 38, 38)
    HINT_COLOR = (148, 163, 184)
    ACCENT = (56, 189, 248)  # cyan accent to distinguish this data-driven scene
    GRAY_INACTIVE = (51, 65, 85)

    font_title = pygame.font.SysFont("arial", 28, bold=True)
    font_prompt = pygame.font.SysFont("arial", 24, bold=True)
    font_passage = pygame.font.SysFont("arial", 22)
    font_choice = pygame.font.SysFont("arial", 20)
    font_explanation = pygame.font.SysFont("arial", 19, italic=True)
    EXPLANATION_COLOR = (203, 213, 225)
    if_right = []

    questions = load_questions_from_df(
        df, domain=domain, difficulty=difficulty, count=count,
        shuffle=shuffle, random_state=random_state
    )
    if not questions:
        print("No questions found in DataFrame for the given domain/difficulty!")
        return 0, 0, []

    correct_count = 0
    q_index = 0
    answered = False
    selected_letter = None
    results = []

    clock = pygame.time.Clock()
    box_width = min(1100, WIDTH - 160)
    start_x = (WIDTH - box_width) // 2

    while q_index < len(questions):
        q_data = questions[q_index]

        paragraph = q_data["paragraph"]
        prompt = q_data["question"]
        choices = q_data["choices"]
        correct_letter = q_data["correct_answer"]
        explanation = q_data["explanation"]

        screen.fill(BG_COLOR)

        # Header & progress bars
        label_bits = []
        if domain is not None:
            label_bits.append(str(domain).upper())
        if difficulty is not None:
            label_bits.append(str(difficulty).upper())
        header_label = f" - {' / '.join(label_bits)}" if label_bits else ""
        title_surf = font_title.render(f"{title}{header_label}", True, ACCENT)
        screen.blit(title_surf, (start_x, 30))

        score_surf = font_choice.render(f"Score: {correct_count}/{len(questions)}", True, TEXT_COLOR)
        screen.blit(score_surf, (start_x + box_width - score_surf.get_width(), 35))

        bar_w = 40
        bar_h = 10
        for i in range(len(questions)):
            bar_rect = pygame.Rect(start_x + i * (bar_w + 10), 75, bar_w, bar_h)
            if i < len(results):
                if results[i]:
                    color = CORRECT_GREEN
                else:
                    color = WRONG_RED

            elif i == q_index:
                color = ACCENT
            else:
                color = GRAY_INACTIVE
            pygame.draw.rect(screen, color, bar_rect, border_radius=5)

        y = 105

        if paragraph:
            for line in wrap_text(paragraph, font_passage, box_width):
                screen.blit(font_passage.render(line, True, TEXT_COLOR), (start_x, y))
                y += 28
            y += 20

        for line in wrap_text(prompt, font_prompt, box_width):
            screen.blit(font_prompt.render(line, True, TEXT_COLOR), (start_x, y))
            y += 32
        y += 20

        choice_boxes = {}
        for letter, text in choices.items():
            full_text = f"{letter}) {text}"
            choice_lines = wrap_text(full_text, font_choice, box_width - 40)
            box_height = 20 + (len(choice_lines) * 26)

            rect = pygame.Rect(start_x, y, box_width, box_height)
            choice_boxes[letter] = rect

            color = CHOICE_BG
            if answered:
                if letter == correct_letter:
                    color = CORRECT_GREEN
                elif letter == selected_letter:
                    color = WRONG_RED

            pygame.draw.rect(screen, color, rect, border_radius=10)

            line_y = rect.y + 10
            for line in choice_lines:
                label = font_choice.render(line, True, TEXT_COLOR)
                screen.blit(label, (rect.x + 20, line_y))
                line_y += 26

            y += box_height + 12

        if answered:
            if explanation.strip():
                y += 10
                explanation_lines = wrap_text(f"Explanation: {explanation}", font_explanation, box_width)
                for line in explanation_lines:
                    screen.blit(font_explanation.render(line, True, EXPLANATION_COLOR), (start_x, y))
                    y += 24
                y += 6

            hint = font_choice.render("Click anywhere to continue to the next question...", True, HINT_COLOR)
            screen.blit(hint, (start_x, y + 10))

        pygame.display.flip()

        click_handled = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not click_handled:
                click_handled = True
                if not answered:
                    for letter, rect in choice_boxes.items():
                        if rect.collidepoint(event.pos):
                            selected_letter = letter
                            answered = True
                            is_correct = (selected_letter == correct_letter)
                            results.append(is_correct)
                            if_right.append(1) if is_correct else if_right.append(0)
                            if is_correct:
                                correct_count += 1
                            break
                else:
                    q_index += 1
                    answered = False
                    selected_letter = None

        clock.tick(30)

    return correct_count, len(questions), if_right

if __name__ == "__main__":
    create_class = dataframe_training.Dataframe_Questions()
    initialize = create_class.question_batch(5, [])
    dataframe = create_class.probs_df
    test_screen = pygame.display.set_mode((1280, 800))
    pygame.display.set_caption("DataFrame Question Scene - Demo")
    score, total, number_right = run_question_scene(test_screen, dataframe, count=5)
    print(f"Game Over! Final Score: {score}/{total}")
    create_class.update_y(number_right)
    pygame.quit()

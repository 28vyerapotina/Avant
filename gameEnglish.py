import pygame
import sys
from english_game import practicetest_generatorEnglish  # Your English question fetcher

pygame.init()


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


def run_english_scene(screen, level_num, count=5):
    """Runs a dedicated English Question Scene."""
    WIDTH, HEIGHT = screen.get_size()

    # English Theme Colors (Deep Violet / Indigo)
    BG_COLOR = (15, 23, 42)
    TEXT_COLOR = (241, 245, 249)
    CHOICE_BG = (30, 41, 59)
    CORRECT_GREEN = (34, 197, 94)
    WRONG_RED = (220, 38, 38)
    HINT_COLOR = (148, 163, 184)
    ENGLISH_ACCENT = (168, 85, 247)  # Purple accent for English
    GRAY_INACTIVE = (51, 65, 85)

    font_title = pygame.font.SysFont("arial", 28, bold=True)
    font_prompt = pygame.font.SysFont("arial", 24, bold=True)
    font_passage = pygame.font.SysFont("arial", 22)
    font_choice = pygame.font.SysFont("arial", 20)

    # Fetch English questions
    questions = practicetest_generatorEnglish(level_num, count)
    if not questions:
        print("No English questions found!")
        return 0, 0

    correct_count = 0
    q_index = 0
    answered = False
    selected_letter = None
    results = []  # Tracks True/False for the top indicator bars

    clock = pygame.time.Clock()
    box_width = min(1100, WIDTH - 160)
    start_x = (WIDTH - box_width) // 2

    while q_index < len(questions):
        q_raw = questions[q_index]
        q_data = q_raw.get('question', q_raw) if isinstance(q_raw, dict) else q_raw

        paragraph = q_data.get('paragraph', '') or q_data.get('passage', '')
        prompt = q_data.get('question', q_data.get('prompt', ''))
        choices = q_data.get('choices', {})
        correct_letter = q_data.get('correct_answer', q_data.get('answer', ''))

        screen.fill(BG_COLOR)

        # 1. Header & Progress Bars
        title_surf = font_title.render(f"📖 ENGLISH READING & WRITING - LEVEL {level_num}", True, ENGLISH_ACCENT)
        screen.blit(title_surf, (start_x, 30))

        score_surf = font_choice.render(f"Score: {correct_count}/{len(questions)}", True, TEXT_COLOR)
        screen.blit(score_surf, (start_x + box_width - score_surf.get_width(), 35))

        # Draw 5 Progress Indicators
        bar_w = 40
        bar_h = 10
        for i in range(len(questions)):
            bar_rect = pygame.Rect(start_x + i * (bar_w + 10), 75, bar_w, bar_h)
            if i < len(results):
                color = CORRECT_GREEN if results[i] else WRONG_RED
            elif i == q_index:
                color = ENGLISH_ACCENT
            else:
                color = GRAY_INACTIVE
            pygame.draw.rect(screen, color, bar_rect, border_radius=5)

        y = 105

        # 2. Passage / Paragraph (Crucial for English questions)
        if paragraph:
            for line in wrap_text(paragraph, font_passage, box_width):
                screen.blit(font_passage.render(line, True, TEXT_COLOR), (start_x, y))
                y += 28
            y += 20

        # 3. Question Prompt
        for line in wrap_text(prompt, font_prompt, box_width):
            screen.blit(font_prompt.render(line, True, TEXT_COLOR), (start_x, y))
            y += 32
        y += 20

        # 4. Multiple Choice Boxes
        choice_boxes = {}
        choice_items = choices.items() if isinstance(choices, dict) else enumerate(choices)

        for item in choice_items:
            letter = item[0] if isinstance(choices, dict) else chr(65 + item[0])
            text = item[1]

            full_text = f"{letter}) {text}"
            choice_lines = wrap_text(full_text, font_choice, box_width - 40)
            box_height = 20 + (len(choice_lines) * 26)

            rect = pygame.Rect(start_x, y, box_width, box_height)
            choice_boxes[letter] = rect

            color = CHOICE_BG
            if answered:
                if str(letter).upper() == str(correct_letter).upper():
                    color = CORRECT_GREEN
                elif str(letter).upper() == str(selected_letter).upper():
                    color = WRONG_RED

            pygame.draw.rect(screen, color, rect, border_radius=10)

            line_y = rect.y + 10
            for line in choice_lines:
                label = font_choice.render(line, True, TEXT_COLOR)
                screen.blit(label, (rect.x + 20, line_y))
                line_y += 26

            y += box_height + 12

        # 5. Click to Next Hint
        if answered:
            hint = font_choice.render("✨ Click anywhere to continue to the next question...", True, HINT_COLOR)
            screen.blit(hint, (start_x, y + 10))

        pygame.display.flip()

        # 6. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not answered:
                    for letter, rect in choice_boxes.items():
                        if rect.collidepoint(event.pos):
                            selected_letter = letter
                            answered = True
                            is_correct = (str(selected_letter).upper() == str(correct_letter).upper())
                            results.append(is_correct)
                            if is_correct:
                                correct_count += 1
                            break
                else:
                    q_index += 1
                    answered = False
                    selected_letter = None

        clock.tick(30)

    return correct_count, len(questions)


if __name__ == "__main__":
    test_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    score, total = run_english_scene(test_screen, level_num=1, count=5)
    print(f"English Game Over! Final Score: {score}/{total}")
    pygame.quit()
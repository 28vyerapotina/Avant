"""
Entry point that ties the question scene and the fighting game together:

  1. The player must answer REQUIRED_CORRECT questions correctly
     (across as many batches as it takes) before the fight unlocks.
  2. The fight then runs. If the player loses, they're sent back to
     more questions before they can retry -- and the retry starts
     with full health, since the fight state (damage rects, sprites,
     etc.) is rebuilt from scratch each time run_fight() is called.
  3. If the player wins, they're asked whether they want to play
     again via an on-screen button. Choosing "No" quits the game;
     choosing "Yes" sends them back through the question gate.
"""

import os
import sys
import pygame as pg

import dataframe_training
import sprite
import simple_cmp_alg
from question_scene import run_question_scene  # doc 1, refactored into a module

REQUIRED_CORRECT = 5
QUESTIONS_PER_BATCH = 5

BG_COLOR = (15, 23, 42)
TEXT_COLOR = (241, 245, 249)
ACCENT = (56, 189, 248)


# ---------------------------------------------------------------------------
# Title / start screen -- blocks until the START button is clicked
# ---------------------------------------------------------------------------

START_BACKGROUND_COLOR = (176, 196, 239)
START_TEXT_COLOR = (255, 255, 255)
START_BUTTON_COLOR = (60, 60, 200)
START_BUTTON_HOVER_COLOR = (90, 90, 210)


def show_start_screen(screen):
    """Title screen for Azure Rivals. Draws every frame but does nothing
    else -- no questions, no fight -- until the player clicks the button."""
    W, H = screen.get_size()
    bg = pg.image.load('azure_rivals_logo.png').convert_alpha()
    bg = pg.transform.scale(bg, (W, H))
    bg_pos = (0, 0)

    title_font = pg.font.SysFont(None, 100)
    button_font = pg.font.SysFont(None, 40)

    button_w, button_h = 260, 80
    button_rect = pg.Rect(
        W // 2 - button_w // 2, H // 2 + 40, button_w, button_h
    )

    clock = pg.time.Clock()

    waiting = True
    while waiting:
        mouse_pos = pg.mouse.get_pos()
        hovering = button_rect.collidepoint(mouse_pos)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and hovering:
                waiting = False  # only the button click breaks the loop

        screen.fill(START_BACKGROUND_COLOR)
        screen.blit(bg, bg_pos)

        button_color = START_BUTTON_HOVER_COLOR if hovering else START_BUTTON_COLOR
        pg.draw.rect(screen, button_color, button_rect, border_radius=12)

        label_surf = button_font.render("START", True, START_TEXT_COLOR)
        screen.blit(
            label_surf,
            (
                button_rect.centerx - label_surf.get_width() // 2,
                button_rect.centery - label_surf.get_height() // 2,
            ),
        )

        pg.display.flip()
        clock.tick(30)


# ---------------------------------------------------------------------------
# Small helper screens
# ---------------------------------------------------------------------------

DATASET_PATHS = {
    "reading": "english_dataset.json",
    "math": "dataMath.json",
}


def show_subject_select_screen(screen):
    """
    Screen shown right after the Azure Rivals title screen. Two buttons,
    Reading and Math -- blocks until one is clicked, then returns the
    matching key into DATASET_PATHS ("reading" or "math") so the caller
    knows which dataset file to load into Dataframe_Questions.
    """
    W, H = screen.get_size()

    title_font = pg.font.SysFont(None, 70)
    button_font = pg.font.SysFont(None, 44)

    button_w, button_h = 300, 90
    gap = 60
    total_w = button_w * 2 + gap
    left_x = W // 2 - total_w // 2

    reading_rect = pg.Rect(left_x, H // 2, button_w, button_h)
    math_rect = pg.Rect(left_x + button_w + gap, H // 2, button_w, button_h)

    clock = pg.time.Clock()

    waiting = True
    choice = None
    while waiting:
        mouse_pos = pg.mouse.get_pos()
        hover_reading = reading_rect.collidepoint(mouse_pos)
        hover_math = math_rect.collidepoint(mouse_pos)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if hover_reading:
                    choice = "reading"
                    waiting = False
                elif hover_math:
                    choice = "math"
                    waiting = False

        screen.fill(START_BACKGROUND_COLOR)

        title_surf = title_font.render("Choose Your Subject", True, START_TEXT_COLOR)
        screen.blit(title_surf, (W // 2 - title_surf.get_width() // 2, H // 3))

        for rect, hovering, label in (
            (reading_rect, hover_reading, "READING"),
            (math_rect, hover_math, "MATH"),
        ):
            color = START_BUTTON_HOVER_COLOR if hovering else START_BUTTON_COLOR
            pg.draw.rect(screen, color, rect, border_radius=12)
            label_surf = button_font.render(label, True, START_TEXT_COLOR)
            screen.blit(
                label_surf,
                (
                    rect.centerx - label_surf.get_width() // 2,
                    rect.centery - label_surf.get_height() // 2,
                ),
            )

        pg.display.flip()
        clock.tick(30)

    return choice


# ---------------------------------------------------------------------------
# Small helper screens
# ---------------------------------------------------------------------------

def show_message(screen, lines, pause_ms=1500, wait_for_click=False):
    """Show one or more lines of centered text, then pause (or wait for a click)."""
    if isinstance(lines, str):
        lines = [lines]

    font = pg.font.SysFont("arial", 32, bold=True)
    small_font = pg.font.SysFont("arial", 20)
    W, H = screen.get_size()

    screen.fill(BG_COLOR)
    total_h = len(lines) * 44
    y = H // 2 - total_h // 2
    for line in lines:
        surf = font.render(line, True, TEXT_COLOR)
        screen.blit(surf, (W // 2 - surf.get_width() // 2, y))
        y += 44

    if wait_for_click:
        hint = small_font.render("Click anywhere to continue...", True, ACCENT)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, y + 20))

    pg.display.flip()

    clock = pg.time.Clock()
    waiting = True
    start = pg.time.get_ticks()
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if wait_for_click and event.type == pg.MOUSEBUTTONDOWN:
                waiting = False
        if not wait_for_click and pg.time.get_ticks() - start >= pause_ms:
            waiting = False
        clock.tick(30)


def show_play_again_screen(screen):
    """
    Shown after the player wins a fight. Draws a "You Won!" message with
    YES / NO buttons and blocks until one is clicked.

    Returns True  -> player clicked YES, run the game loop again.
    Returns False -> player clicked NO, caller should quit the game.
    """
    W, H = screen.get_size()

    title_font = pg.font.SysFont("arial", 60, bold=True)
    button_font = pg.font.SysFont("arial", 40, bold=True)
    prompt_font = pg.font.SysFont("arial", 34)

    button_w, button_h = 220, 80
    gap = 60
    total_w = button_w * 2 + gap
    left_x = W // 2 - total_w // 2
    button_y = H // 2 + 60

    yes_rect = pg.Rect(left_x, button_y, button_w, button_h)
    no_rect = pg.Rect(left_x + button_w + gap, button_y, button_w, button_h)

    clock = pg.time.Clock()

    waiting = True
    result = None
    while waiting:
        mouse_pos = pg.mouse.get_pos()
        hover_yes = yes_rect.collidepoint(mouse_pos)
        hover_no = no_rect.collidepoint(mouse_pos)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if hover_yes:
                    result = True
                    waiting = False
                elif hover_no:
                    result = False
                    waiting = False

        screen.fill(BG_COLOR)

        title_surf = title_font.render("You Won the Fight!", True, TEXT_COLOR)
        screen.blit(title_surf, (W // 2 - title_surf.get_width() // 2, H // 3 - 40))

        prompt_surf = prompt_font.render("Play again?", True, TEXT_COLOR)
        screen.blit(prompt_surf, (W // 2 - prompt_surf.get_width() // 2, H // 3 + 40))

        for rect, hovering, label in (
            (yes_rect, hover_yes, "YES"),
            (no_rect, hover_no, "NO"),
        ):
            color = START_BUTTON_HOVER_COLOR if hovering else START_BUTTON_COLOR
            pg.draw.rect(screen, color, rect, border_radius=12)
            label_surf = button_font.render(label, True, START_TEXT_COLOR)
            screen.blit(
                label_surf,
                (
                    rect.centerx - label_surf.get_width() // 2,
                    rect.centery - label_surf.get_height() // 2,
                ),
            )

        pg.display.flip()
        clock.tick(30)

    return result


# ---------------------------------------------------------------------------
# Question gate
# ---------------------------------------------------------------------------

def gate_questions(screen, question_bank):
    """
    Keep serving question batches until the player has REQUIRED_CORRECT
    cumulative correct answers. Returns only once the gate is passed.
    """
    total_correct = 0

    show_message(
        screen,
        [f"Answer {REQUIRED_CORRECT} questions correctly to unlock the fight!"],
        wait_for_click=True,
    )

    while total_correct < REQUIRED_CORRECT:
        if not question_bank.y:
            # No answer history yet -- can't train the SVM on nothing,
            # so the very first batch is random.
            question_bank.question_batch(QUESTIONS_PER_BATCH, [])
            batch_size = QUESTIONS_PER_BATCH
        else:
            # Use everything answered so far to predict which domain/
            # difficulty combos this user tends to get wrong, and pull
            # specifically from those for the next batch.
            hardest_indices = question_bank.train_and_rank_hardest(QUESTIONS_PER_BATCH)
            question_bank.question_batch(len(hardest_indices), hardest_indices)
            batch_size = len(hardest_indices)

        if batch_size == 0:
            # Question pool is exhausted -- nothing left to serve.
            show_message(screen, ["No more questions left in the bank!"], pause_ms=2000)
            break

        # probs_df accumulates every question ever pulled (it's built with
        # concat and never reset), so only take the batch we just added.
        df = question_bank.probs_df.tail(batch_size)

        correct, total, if_right = run_question_scene(
            screen,
            df,
            count=batch_size,
            shuffle=False,  # df is already exactly this round's batch -- use all of it, in order
            title="ANSWER CORRECTLY TO UNLOCK THE FIGHT",
        )

        # Feed results back into the question bank's own tracking, same as doc 1 did.
        question_bank.update_y(if_right)

        total_correct += correct

        if total_correct < REQUIRED_CORRECT:
            remaining = REQUIRED_CORRECT - total_correct
            show_message(
                screen,
                [
                    f"You got {correct}/{total} correct this round.",
                    f"You need {remaining} more correct answer(s). Try again!",
                ],
                wait_for_click=True,
            )

    show_message(screen, ["You unlocked the fight!", "Get ready..."], pause_ms=1500)


# ---------------------------------------------------------------------------
# Fight scene (adapted from doc 2's main(), but returns a result instead of
# calling sys.exit() on win/loss, and takes an existing screen so it can be
# re-run cleanly with fresh sprites/health each time)
# ---------------------------------------------------------------------------

def run_fight(screen):
    SCREEN_W, SCREEN_H = screen.get_size()
    clock = pg.time.Clock()

    BASE_W, BASE_H = 1920, 1080
    scale_x = SCREEN_W / BASE_W
    scale_y = SCREEN_H / BASE_H

    def sx(val):
        return int(val * scale_x)

    def sy(val):
        return int(val * scale_y)

    pg.event.pump()
    bg = pg.image.load('backgrounds/background2.png').convert_alpha()
    bg = pg.transform.scale(bg, (SCREEN_W, SCREEN_H))
    bg_pos = (0, 0)

    FRAME_DURATION = 70

    pg.event.pump()
    player = sprite.Sprite('blue', 100, 250)
    opp = simple_cmp_alg.ComputerAlgorithm(1700, 250)

    jump = player.jump()
    left = player.move_dir('left', 'move', 3)
    right = player.move_dir('right', 'move', 3)
    kick_R = player.move_dir('right', 'kick', 9)
    kick_L = player.move_dir('left', 'kick', 9)
    punch_R = player.move_dir('right', 'punch', 7)
    punch_L = player.move_dir('left', 'punch', 7)

    jump1 = opp.char.jump()
    left1 = opp.char.move_dir('left', 'move', 3)
    right1 = opp.char.move_dir('right', 'move', 3)
    kick_R1 = opp.char.move_dir('right', 'kick', 9)
    kick_L1 = opp.char.move_dir('left', 'kick', 9)
    punch_R1 = opp.char.move_dir('right', 'punch', 7)
    punch_L1 = opp.char.move_dir('left', 'punch', 7)

    anim_timer = pg.time.get_ticks()
    anim_index = 0
    current_action = None
    active_anim = None

    anim_2timer = pg.time.get_ticks()
    anim_2index = 0
    current_2action = None
    active_2anim = None

    action = None
    player_violent = False
    current_frame = 0
    timer = pg.time.get_ticks()

    action2 = None
    current_2frame = 0
    timer2 = pg.time.get_ticks()
    kick_cooldown = pg.time.get_ticks()
    punch_cooldown = pg.time.get_ticks()
    computer_speed = pg.time.get_ticks()
    choice = None

    kick_cooldown_time_rate = 1500
    punch_cooldown_time_rate = 750

    # Fresh health/damage rects every call = full health on every retry.
    player_health = pg.Rect(sx(500), sy(200), sx(500), sy(50))
    opp_health = pg.Rect(sx(1050), sy(200), sx(500), sy(50))
    player_damage = pg.Rect(sx(500), sy(200), 0, sy(50))
    opp_damage = pg.Rect(sx(1050), sy(200), 0, sy(50))

    while True:
        player.rect.topleft = (player.x_pos, player.y_pos)
        opp.char.rect.topleft = (opp.char.x_pos, opp.char.y_pos)
        keys = pg.key.get_pressed()

        if pg.sprite.collide_mask(player, opp.char) is not None:
            if pg.time.get_ticks() - kick_cooldown >= kick_cooldown_time_rate:
                if action == kick_R or action == kick_L:
                    opp_damage.update(opp_damage.x, opp_damage.y, opp_damage.width + sx(100), opp_damage.height)
                elif action2 == kick_R1 or action2 == kick_L1:
                    player_damage.update(player_damage.x, player_damage.y, player_damage.width + sx(100), player_damage.height)
                kick_cooldown = pg.time.get_ticks()
            if pg.time.get_ticks() - punch_cooldown >= punch_cooldown_time_rate:
                if action == punch_R or action == punch_L:
                    opp_damage.update(opp_damage.x, opp_damage.y, opp_damage.width + sx(50), opp_damage.height)
                elif action2 == punch_R1 or action2 == punch_L1:
                    player_damage.update(player_damage.x, player_damage.y, player_damage.width + sx(50), player_damage.height)
                punch_cooldown = pg.time.get_ticks()

        # --- This is the only real behavior change from doc 2's main():
        # instead of pg.quit()/sys.exit(), report the result back up.
        if opp_damage.width >= sx(500):
            return "player_win"
        if player_damage.width >= sx(500):
            return "player_loss"

        if keys[pg.K_UP]:
            action = jump
        elif keys[pg.K_RIGHT] and keys[pg.K_SPACE]:
            action = kick_R
            player_violent = True
        elif keys[pg.K_LEFT] and keys[pg.K_SPACE]:
            action = kick_L
            player_violent = True
        elif keys[pg.K_LEFT] and keys[pg.K_RSHIFT]:
            action = punch_L
            player_violent = True
        elif keys[pg.K_RIGHT] and keys[pg.K_RSHIFT]:
            action = punch_R
            player_violent = True
        elif keys[pg.K_RIGHT]:
            player.update_pos(5, 0)
            active_anim = right
        elif keys[pg.K_LEFT]:
            player.update_pos(-5, 0)
            active_anim = left
        else:
            active_anim = None

        if choice == 'jump' and action2 is None:
            action2 = jump1
        elif choice == 'kick_L' and action2 is None:
            action2 = kick_L1
        elif choice == 'kick_R' and action2 is None:
            action2 = kick_R1
        elif choice == 'punch_L' and action2 is None:
            action2 = punch_L1
        elif choice == 'punch_R' and action2 is None:
            action2 = punch_R1
        elif choice == 'move_R':
            opp.char.update_pos(5, 0)
            active_2anim = right1
        elif choice == 'move_L':
            opp.char.update_pos(-5, 0)
            active_2anim = left1
        else:
            active_2anim = None

        if active_anim is not None:
            if active_anim is not current_action:
                current_action = active_anim
                anim_index = 0
                anim_timer = pg.time.get_ticks()
            if pg.time.get_ticks() - anim_timer >= FRAME_DURATION:
                anim_timer = pg.time.get_ticks()
                anim_index = (anim_index + 1) % len(active_anim)
            player.image = active_anim[anim_index]
        else:
            current_action = None

        if active_2anim is not None:
            if active_2anim is not current_2action:
                current_2action = active_2anim
                anim_2index = 0
                anim_2timer = pg.time.get_ticks()
            if pg.time.get_ticks() - anim_2timer >= FRAME_DURATION:
                anim_2timer = pg.time.get_ticks()
                anim_2index = (anim_2index + 1) % len(active_2anim)
            opp.char.image = active_2anim[anim_2index]
        else:
            current_2action = None

        if action is not None:
            if current_frame == len(action):
                player.reset_height()
                current_frame = 0
                player.image = action[current_frame]
                player_violent = False
                action = None
            elif pg.time.get_ticks() - timer >= FRAME_DURATION:
                player.image = action[current_frame]
                current_frame += 1
                timer = pg.time.get_ticks()

        opp.x = opp.char.x_pos
        if pg.time.get_ticks() - computer_speed >= 750:
            choice = opp.return_move(player.x_pos, player_violent, kick_cooldown - pg.time.get_ticks())
            computer_speed = pg.time.get_ticks()

        if action2 is not None:
            if current_2frame == len(action2):
                opp.char.reset_height()
                current_2frame = 0
                opp.char.image = action2[current_2frame]
                action2 = None
            elif pg.time.get_ticks() - timer2 >= FRAME_DURATION:
                opp.char.image = action2[current_2frame]
                current_2frame += 1
                timer2 = pg.time.get_ticks()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

        screen.blit(bg, bg_pos)
        screen.blit(opp.char.image, (opp.char.x_pos, opp.char.y_pos))
        screen.blit(player.image, (player.x_pos, player.y_pos))
        pg.draw.rect(screen, pg.Color(40, 200, 50), player_health)
        pg.draw.rect(screen, pg.Color(40, 200, 50), opp_health)
        pg.draw.rect(screen, pg.Color(250, 10, 50), player_damage)
        pg.draw.rect(screen, pg.Color(250, 10, 50), opp_damage)
        pg.display.flip()
        clock.tick(60)


# ---------------------------------------------------------------------------
# Top-level flow
# ---------------------------------------------------------------------------

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pg.init()

    display_info = pg.display.Info()
    SCREEN_W, SCREEN_H = display_info.current_w, display_info.current_h
    screen = pg.display.set_mode((SCREEN_W, SCREEN_H), pg.FULLSCREEN)
    pg.display.set_caption("Azure Rivals")

    show_start_screen(screen)

    subject = show_subject_select_screen(screen)
    question_bank = dataframe_training.Dataframe_Questions(DATASET_PATHS[subject])

    while True:
        gate_questions(screen, question_bank)

        result = run_fight(screen)

        if result == "player_win":
            # Ask via an on-screen YES/NO button whether to play again.
            play_again = show_play_again_screen(screen)
            if not play_again:
                break  # NO clicked -- fall through to pg.quit()/sys.exit() below
            # YES clicked -- loop repeats: gate_questions() runs again,
            # then run_fight() rebuilds a brand-new fight from scratch.
        else:  # "player_loss"
            show_message(
                screen,
                ["You lost that round.", "Answer more questions for another shot!"],
                wait_for_click=True,
            )
            # loop repeats: gate_questions() runs again, then run_fight()
            # is called fresh, which rebuilds player_damage/opp_damage at
            # zero -- i.e. full health -- for the retry.

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
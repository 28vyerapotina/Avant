# this is the one that shows the pygame window and the logo, with the start button, and when clicked, it goes to the combat screen placeholder
import sys
import pygame
import os
from sat_engine import SATEngine
import pygame


# ----------------------------
# Initialize Pygame
# ----------------------------
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Azure Rivals")

clock = pygame.time.Clock()

# ----------------------------
# Colors
# ----------------------------
BACKGROUND_COLOR = (176, 196, 239)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (60, 60, 200)
BUTTON_HOVER_COLOR = (90, 90, 210)

# ----------------------------
# Font
# ----------------------------
font = pygame.font.SysFont(None, 40)

# ----------------------------
# Load Logo
# ----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "azure_rivals_logo.png")

logo_image = pygame.image.load(logo_path)
w, h = logo_image.get_width(), logo_image.get_height()
logo_image = pygame.transform.scale(logo_image, (int(w * 1), int(h * 1)))

logo_rect = logo_image.get_rect(center=(WIDTH//2, 380))

# ----------------------------
# Start Button
# ----------------------------
start_button = pygame.Rect(0, 0, 220, 70)
start_button.center = (WIDTH//2, 500)

# ----------------------------
# Game State
# ----------------------------
current_state = "menu"

# ----------------------------
# Main Game Loop
# ----------------------------
running = True

while running:

    # ------------------------
    # Events
    # ------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if current_state == "menu":

                    if start_button.collidepoint(event.pos):
                        print("Start Clicked!")
                        current_state = "combat"

    # ------------------------
    # Draw Background
    # ------------------------
    screen.fill(BACKGROUND_COLOR)

    # ------------------------
    # MENU
    # ------------------------
    if current_state == "menu":

        screen.blit(logo_image, logo_rect)

        mouse_pos = pygame.mouse.get_pos()

        if start_button.collidepoint(mouse_pos):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        pygame.draw.rect(screen, color, start_button, border_radius=15)
        pygame.draw.rect(screen, TEXT_COLOR, start_button, 2, border_radius=15)

        text = font.render("START", True, TEXT_COLOR)
        text_rect = text.get_rect(center=start_button.center)

        screen.blit(text, text_rect)

    # ------------------------
    # COMBAT PLACEHOLDER
    # ------------------------
    elif current_state == "combat":

        combat_text = font.render(
            "Combat Screen Placeholder",
            True,
            (0, 0, 0)
        )

        combat_rect = combat_text.get_rect(center=(WIDTH//2, HEIGHT//2))

        screen.blit(combat_text, combat_rect)

    # ------------------------
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()

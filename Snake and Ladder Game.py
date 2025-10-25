import pygame
import random
import sys
import time

# --- 1. Game Setup ---

# (Pygame setup)
pygame.init()
pygame.font.init()

# (Screen constants)
SQUARE_SIZE = 60
GRID_SIZE = 10
WINDOW_WIDTH = SQUARE_SIZE * GRID_SIZE
WINDOW_HEIGHT = SQUARE_SIZE * GRID_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT + 100) # +100 for text area
SCREEN = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Snake and Ladder Game")

# (Colors)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (213, 50, 80)
COLOR_GREEN = (0, 177, 106)
COLOR_BLUE = (0, 119, 182)
COLOR_YELLOW = (253, 224, 71)

# (Fonts)
MAIN_FONT = pygame.font.SysFont("Arial", 20)
ROLL_FONT = pygame.font.SysFont("Arial", 30, bold=True)
WIN_FONT = pygame.font.SysFont("Arial", 50, bold=True)

# (Game Logic Setup)
WINNING_SQUARE = 100
SNAKES_AND_LADDERS = {
    # Ladders
    1: 38,  4: 14,  9: 31,  21: 42,  28: 84,  36: 44,  51: 67,  71: 91,  80: 100,
    # Snakes
    17: 7,  54: 34,  62: 19,  64: 60,  87: 24,  93: 73,  95: 75,  98: 79
}

# Player positions (Player 1 is index 0, Player 2 is index 1)
player_positions = [0, 0]
player_colors = [COLOR_RED, COLOR_BLUE]
current_player = 0
last_roll = 0
game_message = "Player 1's Turn. Press SPACE to roll."
game_over = False

# --- 2. Helper Functions ---

def get_square_coords(square_num):
    """
    Calculates the (x, y) pixel coordinates for the center of a given board square.
    The board layout is a 10x10 grid that "snakes" upwards.
    """
    if square_num == 0:
        return (SQUARE_SIZE // 2, WINDOW_HEIGHT - (SQUARE_SIZE // 2))

    # Calculate row and column (0-9)
    # Row 0 is at the bottom (squares 1-10)
    row = (square_num - 1) // GRID_SIZE
    col = (square_num - 1) % GRID_SIZE

    # Even rows (0, 2, 4...) go left-to-right
    if row % 2 == 0:
        x = col * SQUARE_SIZE + (SQUARE_SIZE // 2)
    # Odd rows (1, 3, 5...) go right-to-left
    else:
        x = (GRID_SIZE - 1 - col) * SQUARE_SIZE + (SQUARE_SIZE // 2)
    
    # Y coordinate is calculated from the top, so we reverse the row
    y = (GRID_SIZE - 1 - row) * SQUARE_SIZE + (SQUARE_SIZE // 2)
    
    return (x, y)

def draw_text(text, font, color, surface, x, y, center=False):
    """Helper function to draw text on the screen."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# --- 3. Drawing Functions ---

def draw_board():
    """Draws the 10x10 grid, numbers, snakes, and ladders."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Calculate the square number
            # This logic finds the number for a (row, col) position
            if row % 2 == 0: # Even rows (from top, e.g., 91-100)
                square_num = (GRID_SIZE - 1 - row) * GRID_SIZE + col + 1
            else: # Odd rows (e.g., 81-90)
                square_num = (GRID_SIZE - 1 - row) * GRID_SIZE + (GRID_SIZE - 1 - col) + 1
            
            # Draw the square
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            color = COLOR_WHITE if (row + col) % 2 == 0 else (200, 200, 200) # Checkered pattern
            pygame.draw.rect(SCREEN, color, rect)
            
            # Draw the square number
            draw_text(str(square_num), MAIN_FONT, COLOR_BLACK, SCREEN, rect.x + 5, rect.y + 5)

def draw_snakes_and_ladders():
    """Draws lines for snakes (red) and ladders (green)."""
    for start, end in SNAKES_AND_LADDERS.items():
        start_pos = get_square_coords(start)
        end_pos = get_square_coords(end)
        
        if end > start: # It's a ladder
            color = COLOR_GREEN
            width = 7
        else: # It's a snake
            color = COLOR_RED
            width = 7
        
        pygame.draw.line(SCREEN, color, start_pos, end_pos, width)

def draw_players():
    """Draws circles for both players."""
    # Player 1 (Red)
    pos1 = get_square_coords(player_positions[0])
    # Offset Player 1 to the top-left of the square's center
    pygame.draw.circle(SCREEN, player_colors[0], (pos1[0] - 10, pos1[1] - 10), 15)
    
    # Player 2 (Blue)
    pos2 = get_square_coords(player_positions[1])
    # Offset Player 2 to the bottom-right of the square's center
    pygame.draw.circle(SCREEN, player_colors[1], (pos2[0] + 10, pos2[1] + 10), 15)

def draw_ui():
    """Draws the text area at the bottom of the screen."""
    ui_rect = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, 100)
    pygame.draw.rect(SCREEN, (50, 50, 50), ui_rect)
    
    # Draw game message
    draw_text(game_message, MAIN_FONT, COLOR_WHITE, SCREEN, WINDOW_WIDTH // 2, WINDOW_HEIGHT + 30, center=True)
    
    # Draw last roll
    roll_text = f"Last Roll: {last_roll}" if last_roll > 0 else "Roll: -"
    draw_text(roll_text, ROLL_FONT, COLOR_YELLOW, SCREEN, WINDOW_WIDTH // 2, WINDOW_HEIGHT + 65, center=True)


# --- 4. Main Game Loop ---

def main():
    global current_player, last_roll, game_message, game_over, player_positions

    running = True
    clock = pygame.time.Clock()

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            # --- Handle Player Input ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    
                    # 1. Roll the die
                    last_roll = random.randint(1, 6)
                    player_name = f"Player {current_player + 1}"
                    
                    current_pos = player_positions[current_player]
                    new_pos = current_pos + last_roll
                    
                    game_message = f"{player_name} rolled a {last_roll} and moves from {current_pos} to {new_pos}."
                    
                    # 2. Check for win
                    if new_pos == WINNING_SQUARE:
                        player_positions[current_player] = WINNING_SQUARE
                        game_message = f"🎉 {player_name} WINS! 🎉 (Press SPACE to play again)"
                        game_over = True
                    
                    # 3. Check for overshoot
                    elif new_pos > WINNING_SQUARE:
                        game_message = f"{player_name} rolled a {last_roll}. {new_pos} is too high! Stay at {current_pos}."
                        # Stay at current_pos, switch player
                    
                    # 4. Move normally
                    else:
                        player_positions[current_player] = new_pos
                        
                        # 5. Check for Snakes and Ladders
                        if new_pos in SNAKES_AND_LADDERS:
                            final_pos = SNAKES_AND_LADDERS[new_pos]
                            
                            # We need to update the screen to show the move *before* the snake/ladder
                            # This is a small hack to make the animation feel better
                            draw_all()
                            pygame.display.flip()
                            time.sleep(1) # Pause for 1 sec
                            
                            if final_pos > new_pos: # Ladder
                                game_message = f"{player_name} found a ladder! 🪜 Climbing to {final_pos}."
                            else: # Snake
                                game_message = f"{player_name} hit a snake! 🐍 Sliding to {final_pos}."
                                
                            player_positions[current_player] = final_pos
                            
                            # Check for win *again* in case a ladder goes to 100
                            if final_pos == WINNING_SQUARE:
                                game_message = f"🎉 {player_name} WINS! 🎉 (Press SPACE to play again)"
                                game_over = True

                    # 6. Switch Player (if no win)
                    if not game_over:
                        current_player = (current_player + 1) % len(player_positions) # Toggles 0 and 1
                        game_message += f" | Player {current_player + 1}'s Turn."
                
                # Handle reset
                elif event.key == pygame.K_SPACE and game_over:
                    # Reset the game
                    player_positions = [0, 0]
                    current_player = 0
                    last_roll = 0
                    game_message = "Player 1's Turn. Press SPACE to roll."
                    game_over = False

        # --- Drawing ---
        draw_all()
        
        # --- Update Display ---
        pygame.display.flip()
        
        # --- Frame Rate ---
        clock.tick(30) # Limit to 30 frames per second

def draw_all():
    """A helper to call all drawing functions in order."""
    SCREEN.fill(COLOR_BLACK) # Clear screen
    draw_board()
    draw_snakes_and_ladders()
    draw_players()
    draw_ui()
    
    if game_over:
        # Draw a semi-transparent overlay
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        # Draw win text
        draw_text(f"Player {current_player + 1} Wins!", WIN_FONT, player_colors[current_player], SCREEN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, center=True)
        draw_text("Press SPACE to Play Again", MAIN_FONT, COLOR_WHITE, SCREEN, WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2) + 60, center=True)


# --- 5. Start the Game ---
if __name__ == "__main__":
    main()

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255, 128)
RED = (255, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 60))  # Extra space for button
pygame.display.set_caption("Knight's Tour Game")

# Board representation: -1 for unvisited, numbers for visit order
board = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
knight_pos = (0, 0)  # Starting position
board[0][0] = 0  # Mark starting position
move_count = 1
game_over = False
success = False

# Reset button properties
reset_button = pygame.Rect(WINDOW_SIZE // 2 - 50, WINDOW_SIZE + 10, 100, 40)


def is_safe(x, y):
    """Check if the position is within the board and unvisited"""
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x][y] == -1


def get_legal_moves(x, y):
    """Get all legal moves for the knight from the current position"""
    moves = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
    legal_moves = []
    for dx, dy in moves:
        new_x, new_y = x + dx, y + dy
        if is_safe(new_x, new_y):
            legal_moves.append((new_x, new_y))
    return legal_moves


def reset_game():
    """Reset the game to initial state"""
    global board, knight_pos, move_count, game_over, success
    board = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    knight_pos = (0, 0)
    board[0][0] = 0
    move_count = 1
    game_over = False
    success = False


def draw_board():
    """Draw the chessboard and the knight's position"""
    screen.fill(WHITE)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if board[row][col] != -1:
                # Draw visited squares with a green tint
                pygame.draw.rect(screen, (0, 128, 0, 128),
                                 (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                # Draw move number (except for knight's current position)
                if (row, col) != knight_pos:
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(str(board[row][col]), True, BLACK)
                    screen.blit(text, (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 20))

    # Highlight legal moves
    legal_moves = get_legal_moves(knight_pos[0], knight_pos[1])
    for move in legal_moves:
        pygame.draw.circle(screen, BLUE,
                           ((move[1] + 0.5) * SQUARE_SIZE, (move[0] + 0.5) * SQUARE_SIZE), 10)

    # Draw knight (K) without move number
    font = pygame.font.SysFont(None, 36)
    knight_text = font.render("K", True, RED)
    screen.blit(knight_text, ((knight_pos[1] + 0.5) * SQUARE_SIZE - 10, (knight_pos[0] + 0.5) * SQUARE_SIZE - 15))

    # Display game over message if applicable
    if game_over:
        font = pygame.font.SysFont(None, 48)
        message = "Success!" if success else "No more moves!"
        text = font.render(message, True, BLACK)
        screen.blit(text, (WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2))

        # Draw reset button
        mouse_over = reset_button.collidepoint(pygame.mouse.get_pos())
        button_color = BUTTON_HOVER_COLOR if mouse_over else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, reset_button)
        font = pygame.font.SysFont(None, 30)
        text = font.render("Reset", True, BLACK)
        screen.blit(text, (reset_button.x + 20, reset_button.y + 10))


def handle_click(pos):
    """Handle mouse click to move the knight or reset the game"""
    global knight_pos, move_count, game_over, success
    if game_over:
        if reset_button.collidepoint(pos):
            reset_game()
        return

    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE
    new_pos = (row, col)

    # Check if the clicked position is a legal move
    if new_pos in get_legal_moves(knight_pos[0], knight_pos[1]):
        board[row][col] = move_count
        knight_pos = new_pos
        move_count += 1

        # Check if all squares are visited
        if move_count == BOARD_SIZE * BOARD_SIZE:
            game_over = True
            success = True
        # Check if no more moves are available
        elif not get_legal_moves(row, col):
            game_over = True


if __name__ == "__main__":
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(event.pos)

        draw_board()
        pygame.display.flip()

    pygame.quit()
    sys.exit()
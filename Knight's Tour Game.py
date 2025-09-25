import pygame
import sys
import time
import threading
import random
import math
from typing import List, Tuple, Optional


class KnightTourGame:
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.visited = [[False for _ in range(board_size)] for _ in range(board_size)]
        self.knight_pos = None
        self.previous_pos = None  # Track previous position for arrow display
        self.move_count = 0
        self.game_over = False
        self.won = False

        # Auto-play control
        self.auto_playing = False
        self.auto_thread = None

        # Knight's 8 possible move directions
        self.knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        # Chess notation
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8']

        # Pygame initialization
        pygame.init()
        self.cell_size = 91
        self.label_size = 39
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.info_height = 250

        # Uniform margins around everything
        self.margin = 20

        # Calculate screen size with uniform margins
        self.screen_width = self.board_width + self.label_size * 2 + self.margin * 2
        self.screen_height = self.board_height + self.label_size + self.info_height + self.margin * 2
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Knight's Tour Game")

        # Board offset for labels and margins
        self.board_offset_x = self.label_size + self.margin
        self.board_offset_y = self.margin

        # Color definitions
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_BROWN = (240, 217, 181)
        self.DARK_BROWN = (181, 136, 99)
        self.VISITED_GRAY = (160, 160, 160)
        self.GREEN = (0, 200, 0)
        self.RED = (220, 20, 20)
        self.BLUE = (0, 100, 200)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.DARK_GREEN = (0, 150, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.DARK_RED = (150, 0, 0)
        self.LIGHT_BLUE = (173, 216, 230)
        self.DARKER_BLUE = (135, 206, 235)
        self.DISABLED_GRAY = (169, 169, 169)
        self.ARROW_COLOR = (255, 100, 0)  # Orange-red color for L-shaped arrow

        # Fonts
        self.font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 26)
        self.number_font = pygame.font.Font(None, 47)
        self.number_font.set_bold(True)
        self.big_font = pygame.font.Font(None, 62)
        self.big_font.set_bold(True)
        self.label_font = pygame.font.Font(None, 31)
        self.button_font = pygame.font.Font(None, 31)

        # Button definitions
        self.button_height = 59
        self.button_spacing = 10

        # Calculate button width to fill the screen with uniform margins
        available_width = self.screen_width - (2 * self.margin) - (3 * self.button_spacing)
        self.button_width = available_width // 4

        self.buttons = {
            'next_step': {
                'rect': pygame.Rect(self.margin, 0, self.button_width, self.button_height),
                'text': 'Next Step',
                'color': self.LIGHT_BLUE,
                'hover_color': self.DARKER_BLUE,
                'disabled_color': self.DISABLED_GRAY
            },
            'auto_complete': {
                'rect': pygame.Rect(self.margin + (self.button_width + self.button_spacing), 0, self.button_width,
                                    self.button_height),
                'text': 'Auto Complete',
                'color': self.LIGHT_BLUE,
                'hover_color': self.DARKER_BLUE,
                'disabled_color': self.DISABLED_GRAY
            },
            'stop_auto': {
                'rect': pygame.Rect(self.margin + (self.button_width + self.button_spacing), 0, self.button_width,
                                    self.button_height),
                'text': 'Stop Auto',
                'color': self.LIGHT_BLUE,
                'hover_color': self.DARKER_BLUE,
                'disabled_color': self.DISABLED_GRAY
            },
            'restart': {
                'rect': pygame.Rect(self.margin + 2 * (self.button_width + self.button_spacing), 0, self.button_width,
                                    self.button_height),
                'text': 'Restart Game',
                'color': self.LIGHT_BLUE,
                'hover_color': self.DARKER_BLUE
            },
            'exit': {
                'rect': pygame.Rect(self.margin + 3 * (self.button_width + self.button_spacing), 0, self.button_width,
                                    self.button_height),
                'text': 'Exit Game',
                'color': self.LIGHT_BLUE,
                'hover_color': self.DARKER_BLUE
            }
        }

        # Auto-place knight at a1
        self.auto_start()

    def auto_start(self):
        """Automatically place knight at a1 (left bottom corner)"""
        start_x, start_y = 0, 7
        self.knight_pos = (start_x, start_y)
        self.previous_pos = None  # First move has no previous position
        self.visited[start_y][start_x] = True
        self.board[start_y][start_x] = 1
        self.move_count = 1

    def board_to_chess_notation(self, x: int, y: int) -> str:
        """Convert board coordinates to chess notation"""
        file = self.files[x]
        rank = self.ranks[7 - y]
        return f"{file}{rank}"

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if the move is valid"""
        return (0 <= x < self.board_size and
                0 <= y < self.board_size and
                not self.visited[y][x])

    def get_possible_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get possible moves from current position"""
        possible_moves = []
        for dx, dy in self.knight_moves:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_move(new_x, new_y):
                possible_moves.append((new_x, new_y))
        return possible_moves

    def count_onward_moves(self, x: int, y: int) -> int:
        """Count how many moves are possible from a given position (Warnsdorff's heuristic)"""
        return len(self.get_possible_moves(x, y))

    def get_best_next_move(self) -> Optional[Tuple[int, int]]:
        """Get the best next move using Warnsdorff's heuristic with random selection"""
        if not self.knight_pos or self.game_over:
            return None

        current_x, current_y = self.knight_pos
        possible_moves = self.get_possible_moves(current_x, current_y)

        if not possible_moves:
            return None

        # Use Warnsdorff's heuristic: choose the move that leads to a square
        # with the fewest onward moves
        best_moves = []
        min_onward_moves = float('inf')

        for move_x, move_y in possible_moves:
            onward_moves = self.count_onward_moves(move_x, move_y)
            if onward_moves < min_onward_moves:
                min_onward_moves = onward_moves
                best_moves = [(move_x, move_y)]
            elif onward_moves == min_onward_moves:
                best_moves.append((move_x, move_y))

        # Randomly choose from the best moves
        return random.choice(best_moves) if best_moves else None

    def make_auto_move(self) -> bool:
        """Make one automatic move"""
        if self.game_over or self.auto_playing:
            return False

        next_move = self.get_best_next_move()
        if next_move:
            x, y = next_move
            return self.move_knight(x, y)
        return False

    def auto_complete_game(self):
        """Auto-complete the entire game in a separate thread"""
        self.auto_playing = True

        while self.auto_playing and not self.game_over:
            next_move = self.get_best_next_move()
            if next_move:
                x, y = next_move
                success = self.move_knight(x, y)
                if success:
                    notation = self.board_to_chess_notation(x, y)
                    print(f"Auto move to {notation} - Move {self.move_count}")
                    if self.won:
                        print("AUTO-PLAY: Knight's Tour completed successfully!")
                        break
                    elif self.game_over:
                        print(f"AUTO-PLAY: Game Over! Completed {self.move_count} moves")
                        break
                else:
                    break
            else:
                # No more moves available
                self.game_over = True
                self.won = False
                print(f"AUTO-PLAY: No more moves available! Completed {self.move_count} moves")
                break

            # Wait 0.5 seconds between moves
            time.sleep(0.5)

        self.auto_playing = False

    def start_auto_complete(self):
        """Start auto-complete in a separate thread"""
        if not self.auto_playing and not self.game_over:
            self.auto_thread = threading.Thread(target=self.auto_complete_game)
            self.auto_thread.daemon = True
            self.auto_thread.start()

    def stop_auto_play(self):
        """Stop auto-play"""
        if self.auto_playing:
            print("Stopping auto-play...")
            self.auto_playing = False
            if self.auto_thread and self.auto_thread.is_alive():
                self.auto_thread.join(timeout=1.0)
            print("Auto-play stopped")

    def move_knight(self, x: int, y: int) -> bool:
        """Move knight to specified position"""
        if self.knight_pos is None or self.game_over:
            return False

        current_x, current_y = self.knight_pos
        possible_moves = self.get_possible_moves(current_x, current_y)

        if (x, y) in possible_moves:
            # Record previous position for arrow display
            self.previous_pos = self.knight_pos

            self.knight_pos = (x, y)
            self.visited[y][x] = True
            self.move_count += 1
            self.board[y][x] = self.move_count

            # Check if won
            if self.move_count == self.board_size * self.board_size:
                self.game_over = True
                self.won = True
            # Check if no moves left
            elif not self.get_possible_moves(x, y):
                self.game_over = True
                self.won = False

            return True
        return False

    def reset_game(self):
        """Reset the game"""
        self.stop_auto_play()
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.knight_pos = None
        self.previous_pos = None
        self.move_count = 0
        self.game_over = False
        self.won = False
        self.auto_start()

    def exit_game(self):
        """Exit the game"""
        self.stop_auto_play()
        pygame.quit()
        print("Thanks for playing Knight's Tour!")
        sys.exit()

    def get_cell_from_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Get board cell coordinates from mouse position"""
        mx, my = mouse_pos
        board_mx = mx - self.board_offset_x
        board_my = my - self.board_offset_y

        if 0 <= board_mx < self.board_width and 0 <= board_my < self.board_height:
            x = board_mx // self.cell_size
            y = board_my // self.cell_size
            return (x, y)
        return None

    def is_button_disabled(self, button_name: str) -> bool:
        """Check if a button should be disabled"""
        if self.game_over:
            # When game is over, only restart and exit are enabled
            return button_name not in ['restart', 'exit']
        elif self.auto_playing:
            # When auto-playing, only stop_auto, restart and exit are enabled
            return button_name not in ['stop_auto', 'restart', 'exit']
        else:
            # During normal gameplay, all buttons except stop_auto are enabled
            return button_name == 'stop_auto'

    def draw_l_shaped_arrow(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Draw L-shaped arrow showing knight's last move with thick, semi-transparent style and large triangular arrowhead"""
        if not from_pos or not to_pos:
            return

        from_x, from_y = from_pos
        to_x, to_y = to_pos

        # Calculate screen coordinates for cell centers
        from_screen_x = self.board_offset_x + from_x * self.cell_size + self.cell_size // 2
        from_screen_y = self.board_offset_y + from_y * self.cell_size + self.cell_size // 2
        to_screen_x = self.board_offset_x + to_x * self.cell_size + self.cell_size // 2
        to_screen_y = self.board_offset_y + to_y * self.cell_size + self.cell_size // 2

        # Calculate the L-shaped path
        dx = to_x - from_x
        dy = to_y - from_y

        # Determine the intermediate point for L-shape
        # Knight moves are always 2 squares in one direction and 1 in perpendicular
        if abs(dx) == 2:
            # Move 2 horizontally first, then 1 vertically
            mid_x = from_x + dx
            mid_y = from_y
        else:
            # Move 2 vertically first, then 1 horizontally
            mid_x = from_x
            mid_y = from_y + dy

        mid_screen_x = self.board_offset_x + mid_x * self.cell_size + self.cell_size // 2
        mid_screen_y = self.board_offset_y + mid_y * self.cell_size + self.cell_size // 2

        # Create a surface for semi-transparent drawing
        arrow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Arrow properties
        arrow_width = 15  # Thick arrow body
        arrow_color = (*self.ARROW_COLOR, 180)  # Semi-transparent orange-red
        triangle_size = 35

        # Calculate direction from mid point to destination for arrowhead
        direction_x = to_screen_x - mid_screen_x
        direction_y = to_screen_y - mid_screen_y
        length = math.sqrt(direction_x ** 2 + direction_y ** 2)

        # Calculate shortened arrow body endpoint
        if length > 0:
            # Normalize direction vector
            dir_x = direction_x / length
            dir_y = direction_y / length

            # Shorten the arrow body so it doesn't extend beyond the triangle base
            arrow_body_end_x = to_screen_x - (triangle_size * 0.7) * dir_x
            arrow_body_end_y = to_screen_y - (triangle_size * 0.7) * dir_y
        else:
            arrow_body_end_x = to_screen_x
            arrow_body_end_y = to_screen_y

        # Draw the L-shaped path with thick lines (shortened)
        pygame.draw.line(arrow_surface, arrow_color,
                         (from_screen_x, from_screen_y),
                         (mid_screen_x, mid_screen_y), arrow_width)
        pygame.draw.line(arrow_surface, arrow_color,
                         (mid_screen_x, mid_screen_y),
                         (arrow_body_end_x, arrow_body_end_y), arrow_width)

        # Draw circles at key points
        # Start point (larger circle)
        pygame.draw.circle(arrow_surface, arrow_color,
                           (from_screen_x, from_screen_y), 10)

        # Corner point (medium circle)
        pygame.draw.circle(arrow_surface, arrow_color,
                           (mid_screen_x, mid_screen_y), 8)

        # Draw large triangular arrowhead
        if length > 0:
            # Calculate perpendicular vector (90 degrees rotated)
            perp_x = -dir_y
            perp_y = dir_x

            # Tip of the arrow (at destination)
            tip_x = to_screen_x
            tip_y = to_screen_y

            # Two base points of the isosceles right triangle
            # Move back from tip by triangle_size in the opposite direction
            base_center_x = tip_x - triangle_size * dir_x
            base_center_y = tip_y - triangle_size * dir_y

            # Create two base points perpendicular to the direction
            # For isosceles right triangle, the base width equals the height
            base_half_width = triangle_size / 2

            base_left_x = base_center_x + base_half_width * perp_x
            base_left_y = base_center_y + base_half_width * perp_y
            base_right_x = base_center_x - base_half_width * perp_x
            base_right_y = base_center_y - base_half_width * perp_y

            # Draw filled triangular arrowhead
            triangle_points = [
                (tip_x, tip_y),
                (base_left_x, base_left_y),
                (base_right_x, base_right_y)
            ]
            pygame.draw.polygon(arrow_surface, arrow_color, triangle_points)

            # Add a small circle at the arrow tip for extra emphasis
            pygame.draw.circle(arrow_surface, arrow_color,
                               (int(tip_x), int(tip_y)), 4)

        # Blit the semi-transparent arrow surface to the main screen
        self.screen.blit(arrow_surface, (0, 0))

    def handle_button_click(self, mouse_pos: Tuple[int, int]):
        """Handle button clicks"""
        info_y = self.board_height + self.label_size + self.margin
        button_y = info_y + 169

        # Check the active buttons only to avoid collision
        active_buttons = []

        # Always add these buttons
        active_buttons.append('next_step')
        active_buttons.append('restart')
        active_buttons.append('exit')

        # Add either auto_complete or stop_auto, not both
        if self.auto_playing:
            active_buttons.insert(-2, 'stop_auto')  # Insert before restart
        else:
            active_buttons.insert(-2, 'auto_complete')  # Insert before restart

        # Check clicks only for active buttons
        for button_name in active_buttons:
            if button_name in self.buttons:
                button_info = self.buttons[button_name]
                button_rect = button_info['rect'].copy()
                button_rect.y = button_y

                if button_rect.collidepoint(mouse_pos):
                    # Check if button is disabled
                    if self.is_button_disabled(button_name):
                        continue  # Skip disabled buttons

                    if button_name == 'next_step':
                        if not self.auto_playing and not self.game_over:
                            success = self.make_auto_move()
                            if success:
                                notation = self.board_to_chess_notation(*self.knight_pos)
                                print(f"Auto move to {notation} - Move {self.move_count}")
                                if self.won:
                                    print("Knight's Tour completed!")
                                elif self.game_over:
                                    print(f"Game Over! Completed {self.move_count} moves")
                            else:
                                print("No valid moves available!")

                    elif button_name == 'auto_complete' and not self.auto_playing and not self.game_over:
                        print("Starting auto-complete...")
                        self.start_auto_complete()

                    elif button_name == 'stop_auto' and self.auto_playing:
                        self.stop_auto_play()

                    elif button_name == 'restart':
                        print("Game reset - Knight placed at a1")
                        self.reset_game()

                    elif button_name == 'exit':
                        self.exit_game()

                    return True
        return False

    def draw_coordinate_labels(self):
        """Draw chess coordinate labels around the board"""
        # Draw file labels (a-h) at bottom
        for i, file_letter in enumerate(self.files):
            x = self.board_offset_x + i * self.cell_size + self.cell_size // 2
            y = self.board_height + self.board_offset_y + 13
            text = self.label_font.render(file_letter, True, self.BLACK)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)

        # Draw rank labels (1-8) at left side
        for i, rank_number in enumerate(self.ranks):
            x = self.margin + 20
            y = self.board_offset_y + (7 - i) * self.cell_size + self.cell_size // 2
            text = self.label_font.render(rank_number, True, self.BLACK)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)

    def draw_buttons(self):
        """Draw control buttons"""
        info_y = self.board_height + self.label_size + self.margin
        button_y = info_y + 169

        mouse_pos = pygame.mouse.get_pos()

        # Determine which buttons to show
        buttons_to_show = ['next_step', 'restart', 'exit']
        if self.auto_playing:
            buttons_to_show.insert(-2, 'stop_auto')
        else:
            buttons_to_show.insert(-2, 'auto_complete')

        for button_name in buttons_to_show:
            if button_name in self.buttons:
                button_info = self.buttons[button_name]
                button_rect = button_info['rect'].copy()
                button_rect.y = button_y

                # Check if button is disabled
                is_disabled = self.is_button_disabled(button_name)

                # Determine button color
                if is_disabled:
                    color = button_info['disabled_color']
                elif button_rect.collidepoint(mouse_pos) and not is_disabled:
                    color = button_info['hover_color']
                else:
                    color = button_info['color']

                # Draw button
                pygame.draw.rect(self.screen, color, button_rect)
                pygame.draw.rect(self.screen, self.BLACK, button_rect, 3)

                # Draw button text
                text_color = self.GRAY if is_disabled else self.BLACK
                text = self.button_font.render(button_info['text'], True, text_color)
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)

    def draw_board(self):
        """Draw the chess board"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = self.board_offset_x + col * self.cell_size
                y = self.board_offset_y + row * self.cell_size

                # Determine cell color
                if self.visited[row][col]:
                    color = self.VISITED_GRAY
                else:
                    if (row + col) % 2 == 0:
                        color = self.LIGHT_BROWN
                    else:
                        color = self.DARK_BROWN

                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, self.BLACK, (x, y, self.cell_size, self.cell_size), 2)

                # If cell is visited, show move number
                if self.visited[row][col]:
                    text = self.number_font.render(str(self.board[row][col]), True, self.BLACK)
                    text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(text, text_rect)

        # Draw possible move positions (only if not auto-playing and not game over)
        if self.knight_pos and not self.game_over and not self.auto_playing:
            current_x, current_y = self.knight_pos
            possible_moves = self.get_possible_moves(current_x, current_y)
            for px, py in possible_moves:
                x = self.board_offset_x + px * self.cell_size
                y = self.board_offset_y + py * self.cell_size
                border_size = 5
                circle_size = 13
                pygame.draw.rect(self.screen, self.GREEN,
                                 (x + border_size, y + border_size,
                                  self.cell_size - 2 * border_size, self.cell_size - 2 * border_size),
                                 border_size)
                pygame.draw.circle(self.screen, self.GREEN,
                                   (x + self.cell_size // 2, y + self.cell_size // 2), circle_size)

        # Draw knight position FIRST
        if self.knight_pos:
            kx, ky = self.knight_pos
            x = self.board_offset_x + kx * self.cell_size
            y = self.board_offset_y + ky * self.cell_size

            knight_radius = self.cell_size // 3
            pygame.draw.circle(self.screen, self.RED,
                               (x + self.cell_size // 2, y + self.cell_size // 2),
                               knight_radius)
            pygame.draw.circle(self.screen, self.WHITE,
                               (x + self.cell_size // 2, y + self.cell_size // 2),
                               knight_radius - 5)

            knight_text = self.big_font.render("K", True, self.BLACK)
            knight_rect = knight_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
            self.screen.blit(knight_text, knight_rect)

        # Draw L-shaped arrow AFTER knight (so it appears on top)
        if self.previous_pos and self.knight_pos and self.move_count > 1:
            self.draw_l_shaped_arrow(self.previous_pos, self.knight_pos)

    def draw_info(self):
        """Draw game information"""
        info_y = self.board_height + self.label_size + self.margin
        pygame.draw.rect(self.screen, self.WHITE, (0, info_y, self.screen_width, self.info_height))
        pygame.draw.line(self.screen, self.BLACK, (0, info_y), (self.screen_width, info_y), 3)

        # Move counter with current position
        if self.knight_pos:
            current_notation = self.board_to_chess_notation(*self.knight_pos)
            move_text = f"Moves: {self.move_count} / 64 | Current Position: {current_notation}"
        else:
            move_text = f"Moves: {self.move_count} / 64"

        text_surface = self.font.render(move_text, True, self.BLACK)
        self.screen.blit(text_surface, (self.margin, info_y + 26))

        # Progress bar
        progress = self.move_count / 64
        bar_width = self.screen_width - 2 * self.margin
        bar_height = 26
        bar_x = self.margin
        bar_y = info_y + 78

        pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
        if progress > 0:
            fill_width = int(bar_width * progress)
            color = self.GREEN if self.won else self.BLUE
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_width, bar_height), 3)

        # Game status text
        if self.auto_playing:
            status_text = "Auto-playing... Click 'Stop Auto' to stop"
            color = self.ORANGE
        elif self.game_over:
            if self.won:
                status_text = "Congratulations! You win! Click 'Restart' to play again"
                color = self.GREEN
            else:
                status_text = "Game Over! Knight is trapped! Click 'Restart' to try again"
                color = self.RED
        else:
            possible_count = len(self.get_possible_moves(*self.knight_pos))
            status_text = f"Click green positions to move knight ({possible_count} choices)"
            color = self.BLACK

        status_surface = self.font.render(status_text, True, color)
        self.screen.blit(status_surface, (self.margin, info_y + 124))


    def run(self):
        """Run the main game loop"""
        clock = pygame.time.Clock()
        running = True

        print("Knight's Tour Game Started!")
        print("Game Rules:")
        print("   - Knight starts at a1 (left bottom corner)")
        print("   - Knight moves in L-shape (like in chess)")
        print("   - Visit every cell on the board exactly once")
        print("   - Green positions show where you can move")
        print("   - Gray cells show visited positions with move numbers")
        print("   - Goal: Complete all 64 squares!")
        print(f"\nKnight placed at a1")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check button clicks first
                        if self.handle_button_click(event.pos):
                            continue

                        # Then check board clicks (only if not auto-playing and not game over)
                        if not self.auto_playing and not self.game_over:
                            cell = self.get_cell_from_mouse(event.pos)
                            if cell:
                                x, y = cell
                                if self.move_knight(x, y):
                                    notation = self.board_to_chess_notation(x, y)
                                    print(f"Knight moved to {notation} - Move {self.move_count}")
                                    if self.won:
                                        print("CONGRATULATIONS! You completed the Knight's Tour!")
                                    elif self.game_over:
                                        print(f"Game Over! Completed {self.move_count} moves")
                                else:
                                    print("Invalid move! Please click on green highlighted positions")

            # Draw game screen
            self.screen.fill(self.WHITE)
            self.draw_coordinate_labels()
            self.draw_board()
            self.draw_info()
            self.draw_buttons()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        print("Thanks for playing Knight's Tour!")
        sys.exit()


if __name__ == "__main__":
    try:
        game = KnightTourGame(8)
        game.run()
    except ImportError:
        print("Error: pygame not installed!")
        print("Please run: pip install pygame")
    except Exception as e:
        print(f"Game error: {e}")

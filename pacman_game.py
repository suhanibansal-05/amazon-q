import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 25
MAZE_WIDTH = WINDOW_WIDTH // CELL_SIZE
MAZE_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)

# Game states
WALL = 1
PATH = 0
DOT = 2

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.move_counter = 0

    def get_valid_moves(self, maze):
        """Get list of valid moves for the ghost"""
        valid_moves = []
        directions = [
            ('up', 0, -1),
            ('down', 0, 1),
            ('left', -1, 0),
            ('right', 1, 0)
        ]

        for direction, dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            # Check bounds and walls
            if (0 <= new_x < MAZE_WIDTH and
                0 <= new_y < MAZE_HEIGHT and
                maze[new_y][new_x] != WALL):
                valid_moves.append((direction, new_x, new_y))

        return valid_moves

    def move(self, maze):
        """Move the ghost randomly through the maze"""
        self.move_counter += 1

        # Move every 15 frames (slower than player)
        if self.move_counter < 15:
            return

        self.move_counter = 0
        valid_moves = self.get_valid_moves(maze)

        if not valid_moves:
            return

        # 70% chance to continue in same direction if possible
        current_direction_moves = [move for move in valid_moves if move[0] == self.direction]

        if current_direction_moves and random.random() < 0.7:
            chosen_move = current_direction_moves[0]
        else:
            # Choose random direction
            chosen_move = random.choice(valid_moves)

        self.direction, self.x, self.y = chosen_move

class PacManGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man Game")
        self.clock = pygame.time.Clock()

        # Player position (in grid coordinates)
        self.player_x = 1
        self.player_y = 1

        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        # Game state
        self.game_over = False
        self.game_won = False

        # Create maze
        self.create_maze()

        # Create ghosts
        self.ghosts = []
        self.spawn_ghosts()

    def create_maze(self):
        """Create a simple maze layout"""
        # Initialize maze with walls
        self.maze = [[WALL for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]

        # Create paths and place dots
        # Simple maze pattern - you can customize this
        for y in range(1, MAZE_HEIGHT - 1):
            for x in range(1, MAZE_WIDTH - 1):
                # Create corridors
                if (x % 2 == 1 and y % 2 == 1) or \
                   (x % 4 == 1 and y % 2 == 0) or \
                   (x % 2 == 0 and y % 4 == 1):
                    self.maze[y][x] = DOT

        # Create some additional paths
        for y in range(2, MAZE_HEIGHT - 2, 3):
            for x in range(2, MAZE_WIDTH - 2):
                if x % 3 != 0:
                    self.maze[y][x] = DOT

        # Ensure player starting position is clear
        self.maze[self.player_y][self.player_x] = PATH

        # Create some larger open areas
        for y in range(5, 10):
            for x in range(5, 15):
                if (x + y) % 3 != 0:
                    self.maze[y][x] = DOT

    def spawn_ghosts(self):
        """Spawn ghosts in valid positions"""
        ghost_colors = [RED, PINK]
        ghost_positions = []

        # Find valid spawn positions (away from player)
        attempts = 0
        while len(ghost_positions) < 2 and attempts < 100:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Check if position is valid and not too close to player
            if (self.maze[y][x] != WALL and
                abs(x - self.player_x) + abs(y - self.player_y) > 5 and
                (x, y) not in ghost_positions):
                ghost_positions.append((x, y))

            attempts += 1

        # Create ghosts
        for i, (x, y) in enumerate(ghost_positions):
            color = ghost_colors[i % len(ghost_colors)]
            self.ghosts.append(Ghost(x, y, color))

    def handle_input(self):
        """Handle player input for movement"""
        if self.game_over or self.game_won:
            return

        keys = pygame.key.get_pressed()
        new_x, new_y = self.player_x, self.player_y

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x = max(0, self.player_x - 1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x = min(MAZE_WIDTH - 1, self.player_x + 1)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y = max(0, self.player_y - 1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y = min(MAZE_HEIGHT - 1, self.player_y + 1)

        # Check if new position is valid (not a wall)
        if self.maze[new_y][new_x] != WALL:
            # Check if there's a dot to collect
            if self.maze[new_y][new_x] == DOT:
                self.score += 10
                self.maze[new_y][new_x] = PATH

            self.player_x = new_x
            self.player_y = new_y

    def check_ghost_collision(self):
        """Check if Pac-Man collides with any ghost"""
        for ghost in self.ghosts:
            if self.player_x == ghost.x and self.player_y == ghost.y:
                self.game_over = True
                return True
        return False

    def update_ghosts(self):
        """Update ghost positions"""
        if not self.game_over and not self.game_won:
            for ghost in self.ghosts:
                ghost.move(self.maze)

    def draw(self):
        """Draw the game"""
        self.screen.fill(BLACK)

        # Draw maze
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if self.maze[y][x] == WALL:
                    pygame.draw.rect(self.screen, BLUE, rect)
                elif self.maze[y][x] == DOT:
                    # Draw dot in center of cell
                    center_x = x * CELL_SIZE + CELL_SIZE // 2
                    center_y = y * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 3)

        # Draw ghosts
        for ghost in self.ghosts:
            ghost_center_x = ghost.x * CELL_SIZE + CELL_SIZE // 2
            ghost_center_y = ghost.y * CELL_SIZE + CELL_SIZE // 2

            # Draw ghost body (circle)
            pygame.draw.circle(self.screen, ghost.color, (ghost_center_x, ghost_center_y), CELL_SIZE // 2 - 2)

            # Draw ghost eyes
            eye_size = 3
            left_eye_x = ghost_center_x - 6
            right_eye_x = ghost_center_x + 6
            eye_y = ghost_center_y - 4
            pygame.draw.circle(self.screen, WHITE, (left_eye_x, eye_y), eye_size)
            pygame.draw.circle(self.screen, WHITE, (right_eye_x, eye_y), eye_size)
            pygame.draw.circle(self.screen, BLACK, (left_eye_x, eye_y), 1)
            pygame.draw.circle(self.screen, BLACK, (right_eye_x, eye_y), 1)

        # Draw player (Pac-Man)
        player_center_x = self.player_x * CELL_SIZE + CELL_SIZE // 2
        player_center_y = self.player_y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, YELLOW, (player_center_x, player_center_y), CELL_SIZE // 2 - 2)

        # Draw a simple "mouth" for Pac-Man
        mouth_points = [
            (player_center_x, player_center_y),
            (player_center_x + CELL_SIZE // 3, player_center_y - 5),
            (player_center_x + CELL_SIZE // 3, player_center_y + 5)
        ]
        pygame.draw.polygon(self.screen, BLACK, mouth_points)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over or win message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press ESC to exit", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
            self.screen.blit(game_over_text, text_rect)
        elif self.game_won:
            win_text = self.font.render("YOU WIN! Press ESC to exit", True, WHITE)
            text_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
            self.screen.blit(win_text, text_rect)

        # Draw instructions
        if not self.game_over and not self.game_won:
            instruction_text = pygame.font.Font(None, 24).render("Use Arrow Keys or WASD to move. Avoid ghosts!", True, WHITE)
            self.screen.blit(instruction_text, (10, WINDOW_HEIGHT - 30))

        pygame.display.flip()

    def check_win_condition(self):
        """Check if all dots have been collected"""
        for row in self.maze:
            if DOT in row:
                return False
        self.game_won = True
        return True

    def run(self):
        """Main game loop"""
        running = True
        move_delay = 0

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Handle movement with delay to prevent too fast movement
            if move_delay <= 0:
                self.handle_input()
                move_delay = 8  # Adjust this value to change movement speed
            else:
                move_delay -= 1

            # Update ghosts
            self.update_ghosts()

            # Check ghost collision
            self.check_ghost_collision()

            # Check win condition
            if not self.game_over:
                self.check_win_condition()

            self.draw()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PacManGame()
    game.run()
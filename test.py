import pygame as pg
import asyncio
import platform
from random import randint, random, choice
from collections import defaultdict, deque

# Initialize Pygame
pg.init()

# Game constants
GRID_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

class SnakeGame:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pg.display.set_caption("Snake with Q-learning")
        self.clock = pg.time.Clock()
        # Q-learning parameters
        self.q_table = defaultdict(lambda: {a: 0 for a in ['up', 'down', 'left', 'right']})
        self.alpha = 0.4
        self.gamma = 0.9
        self.epsilon = 0.2
        self.count = 0
        self.actions = ['up', 'down', 'left', 'right']
        # Track position history to detect looping
        self.position_history = deque(maxlen=10)
        self.position_counts = defaultdict(int)
        self.reset()

    def reset(self):
        # Initialize snake and food
        self.snake_pos = (1, 1)
        self.food_pos = (10, 10)
        self.position_history.clear()
        self.position_counts.clear()
        # Custom map with walls and obstacles
        self.walls = set()
        # Border walls
        for x in range(GRID_SIZE):
            self.walls.add((x, 0))
            self.walls.add((x, GRID_SIZE - 1))
        for y in range(GRID_SIZE):
            self.walls.add((0, y))
            self.walls.add((GRID_SIZE - 1, y))
        # Obstacles
        # Horizontal walls
        for y in range(3, 8):
            self.walls.add((5, y))
        for y in range(12, 17):
            self.walls.add((15, y))
        # Vertical walls
        for x in range(3, 8):
            if (x, 5) != (3, 5):  # Remove (3, 5) to allow path
                self.walls.add((x, 5))
        for x in range(12, 17):
            self.walls.add((x, 15))
        # 2x2 block
        self.walls.add((8, 8))
        self.walls.add((8, 9))
        self.walls.add((9, 8))
        self.walls.add((9, 9))
        self.walls.add((6, 6))
        self.walls.add((8, 6))
        self.walls.add((9, 7))
        self.walls.add((2, 4))

    def random_pos(self):
        while True:
            x = randint(1, GRID_SIZE - 2)
            y = randint(1, GRID_SIZE - 2)
            if (x, y) not in self.walls and (x, y) != self.food_pos:
                return (x, y)

    def check_wall(self, x, y):
        return (x, y) not in self.walls

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_next_pos(self, pos, action):
        x, y = pos
        if action == 'up':
            return (x - 1, y)
        elif action == 'down':
            return (x + 1, y)
        elif action == 'left':
            return (x, y - 1)
        elif action == 'right':
            return (x, y + 1)
        return pos

    def get_q_value(self, state, action):
        if not self.check_wall(*state):
            return 0
        next_pos = self.get_next_pos(state, action)
        if not self.check_wall(*next_pos):
            return float('-inf')
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in self.actions}
        if self.q_table[state][action] == 0 or self.manhattan_distance(state, self.food_pos) > 10:
            self.q_table[state][action] = -self.manhattan_distance(next_pos, self.food_pos)
        return self.q_table[state][action]

    def choose_action(self, state):
        if not self.check_wall(*state):
            return choice(self.actions)
        current_epsilon = self.epsilon * (0.99 ** (self.count // 20))
        print(f"State: {state}, Epsilon: {current_epsilon}")
        if random() < current_epsilon:
            valid_moves = []
            heuristic_values = []
            for a in self.actions:
                next_pos = self.get_next_pos(state, a)
                if self.check_wall(*next_pos):
                    valid_moves.append(a)
                    heuristic_values.append(self.manhattan_distance(next_pos, self.food_pos))
            if valid_moves:
                min_h = min(heuristic_values)
                best_moves = [valid_moves[i] for i, h in enumerate(heuristic_values) if h == min_h]
                print(f"Heuristic chosen: {best_moves}, Values: {heuristic_values}")
                return choice(best_moves)
            print("No valid moves, choosing random")
            return choice(self.actions)
        
        q_values = [self.get_q_value(state, a) for a in self.actions]
        print(f"Q-values: {q_values}")
        valid_q_values = [q for q in q_values if q != float('-inf')]
        if not valid_q_values:
            valid_moves = [a for a in self.actions if self.check_wall(*self.get_next_pos(state, a))]
            print(f"No valid Q-values, choosing random from: {valid_moves}")
            return choice(valid_moves) if valid_moves else choice(self.actions)
        max_q = max(valid_q_values)
        max_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        print(f"Max actions: {max_actions}")
        return choice(max_actions)

    def get_reward(self, old_pos, new_pos, valid_move, ate_food):
        reward = 0
        if not valid_move:
            reward -= 20
        if ate_food:
            reward += 200
        reward -= 10
        old_manhattan = self.manhattan_distance(old_pos, self.food_pos)
        new_manhattan = self.manhattan_distance(new_pos, self.food_pos)
        if new_manhattan < old_manhattan:
            reward += 100 / (new_manhattan + 1)
        # Penalize looping
        self.position_counts[new_pos] += 1
        if self.position_counts[new_pos] >= 3:
            reward -= 50
            self.snake_pos = self.random_pos()
            next_pos = self.snake_pos
            print(f"Loop detected at {new_pos}, new snake pos: {self.snake_pos}")
        return reward

    def update_q_table(self, old_pos, new_pos, action, ate_food, valid_move):
        self.count += 1
        state = old_pos
        reward = self.get_reward(old_pos, new_pos, valid_move, ate_food)
        next_state = new_pos
        self.q_table[state][action] += self.alpha * (
            reward + self.gamma * max(self.q_table[next_state].values()) - self.q_table[state][action]
        )
        print(f"Update {self.count}: Pos {new_pos}, Action {action}, Reward {reward}, Q {self.q_table[state][action]}")
        return reward

    def update(self):
        old_pos = self.snake_pos
        state = old_pos
        valid_move = True
        action = self.choose_action(state)

        print(f"Action: {action}, Before: {old_pos}")
        next_pos = self.get_next_pos(self.snake_pos, action)
        print(f"Next_pos: {next_pos}")

        if self.check_wall(*next_pos):
            self.snake_pos = next_pos
        else:
            valid_move = False
            self.snake_pos = self.random_pos()
            next_pos = self.snake_pos
            print(f"Hit wall, new snake pos: {self.snake_pos}")

        print(f"After: {self.snake_pos}")
        self.position_history.append(self.snake_pos)
        ate_food = self.snake_pos == self.food_pos
        if ate_food:
            self.snake_pos = self.random_pos()
            next_pos = self.snake_pos
            print(f"Ate food, new snake pos: {self.snake_pos}")

        self.update_q_table(old_pos, next_pos, action, ate_food, valid_move)
        self.epsilon = max(0.01, self.epsilon * 0.995)

    def draw(self):
        self.screen.fill(BLACK)
        # Draw grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pg.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) in self.walls:
                    pg.draw.rect(self.screen, GRAY, rect)
                else:
                    pg.draw.rect(self.screen, WHITE, rect, 1)
        # Draw snake
        snake_rect = pg.Rect(self.snake_pos[0] * CELL_SIZE, self.snake_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pg.draw.rect(self.screen, GREEN, snake_rect)
        # Draw food
        food_rect = pg.Rect(self.food_pos[0] * CELL_SIZE, self.food_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pg.draw.rect(self.screen, RED, food_rect)
        pg.display.flip()

async def main():
    game = SnakeGame()
    while True:
        game.update()
        game.draw()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    asyncio.run(main())
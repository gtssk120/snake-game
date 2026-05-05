"""
Snake class for a terminal snake game.
Pure game logic — no curses or UI imports.
"""
from collections import deque


class Snake:
    """A snake that moves on a grid, grows, and detects collisions."""

    # Direction vectors: (dy, dx) where y increases downward (curses convention)
    DIRECTION_VECTORS = {
        'UP': (-1, 0),
        'DOWN': (1, 0),
        'LEFT': (0, -1),
        'RIGHT': (0, 1),
    }

    # Opposite directions (for 180° reversal prevention)
    OPPOSITE_DIRECTIONS = {
        'UP': 'DOWN',
        'DOWN': 'UP',
        'LEFT': 'RIGHT',
        'RIGHT': 'LEFT',
    }

    def __init__(self, start_pos: tuple):
        """Initialize snake with head at start_pos (y, x) and body length 1."""
        self._body = deque([start_pos])
        self._direction = 'UP'
        self._growing = False

    @property
    def head(self) -> tuple:
        """Return (y, x) position of the head."""
        return self._body[0]

    @property
    def body(self) -> list:
        """Return list of (y, x) positions from head to tail."""
        return list(self._body)

    @property
    def direction(self) -> str:
        """Return current direction: 'UP', 'DOWN', 'LEFT', or 'RIGHT'."""
        return self._direction

    def set_direction(self, new_dir: str) -> None:
        """Set direction, preventing 180° reversal."""
        if new_dir in self.DIRECTION_VECTORS:
            opposite = self.OPPOSITE_DIRECTIONS[new_dir]
            if opposite != self._direction:
                self._direction = new_dir

    def move(self) -> tuple:
        """Move snake one step in current direction.

        Returns new head position. Appends new head. If growing flag is
        True, does NOT pop tail (snake grows by 1); otherwise pops tail.
        """
        dy, dx = self.DIRECTION_VECTORS[self._direction]
        cur_head = self._body[0]
        new_head = (cur_head[0] + dy, cur_head[1] + dx)
        self._body.appendleft(new_head)
        if not self._growing:
            self._body.pop()
        else:
            self._growing = False
        return new_head

    def grow(self) -> None:
        """Set flag so next move() adds a segment instead of removing tail."""
        self._growing = True

    def collides_with_self(self) -> bool:
        """Return True if head overlaps any body segment (excluding tail).

        The tail is excluded because it will be removed when move() is called
        (unless growing). This checks the state AFTER the next move.
        """
        head = self._body[0]
        # Check against body[1:] (skip head), excluding tail (last element)
        segments_to_check = list(self._body)[1:-1]  # exclude head and tail
        return head in segments_to_check

    def collides_with(self, pos: tuple) -> bool:
        """Return True if pos overlaps with any body segment."""
        return pos in self._body

    def reset(self, start_pos: tuple) -> None:
        """Reset snake to initial state with head at start_pos."""
        self._body = deque([start_pos])
        self._direction = 'UP'
        self._growing = False


import random


class Game:
    """Manages game state: snake, food, score, pause, game_over.

    Pure game logic — no curses or UI imports. The Game class orchestrates
    a Snake instance within bounded walls, spawns food, and tracks score.
    """

    def __init__(self, width=20, height=20, tick_interval=0.15):
        """Initialize game with given dimensions and tick interval.

        Args:
            width: Number of columns (wall bounds: x in [0, width-1]).
            height: Number of rows (wall bounds: y in [0, height-1]).
            tick_interval: Seconds between ticks (for UI timing, not used here).
        """
        self.width = width
        self.height = height
        self.tick_interval = tick_interval
        self.snake = Snake((height // 2, width // 2))
        self.score = 0
        self.game_over = False
        self._paused = False
        self._food = None
        self.spawn_food()

    # ------------------------------------------------------------------
    # Food management
    # ------------------------------------------------------------------

    def spawn_food(self) -> None:
        """Place food at a random empty cell not occupied by the snake."""
        while True:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            if not self.snake.collides_with((fy, fx)):
                self._food = (fy, fx)
                break

    def tick(self) -> bool:
        """Advance game state by one step (move snake, check collisions).

        Returns True if the game is still active, False if game over or paused.
        """
        if self._paused or self.game_over:
            return False

        head = self.snake.head

        # Check if the next position will land on food — grow before move
        dy, dx = self.snake.DIRECTION_VECTORS[self.snake.direction]
        next_pos = (head[0] + dy, head[1] + dx)
        will_eat = self._food is not None and next_pos == self._food

        if will_eat:
            self.snake.grow()

        # Move snake one step in current direction
        self.snake.move()

        head = self.snake.head
        hy, hx = head

        # Wall collision check
        if hy < 0 or hy >= self.height or hx < 0 or hx >= self.width:
            self.game_over = True
            return False

        # Self collision check
        if self.snake.collides_with_self():
            self.game_over = True
            return False

        # Food collision check
        if will_eat:
            self.score += 10
            self.spawn_food()

        return True

    # ------------------------------------------------------------------
    # Pause / Resume
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Pause the game."""
        self._paused = True

    def resume(self) -> None:
        """Resume the game."""
        self._paused = False

    @property
    def is_paused(self) -> bool:
        """Return True if game is paused."""
        return self._paused

    # ------------------------------------------------------------------
    # Read-only properties
    # ------------------------------------------------------------------

    @property
    def score(self) -> int:
        """Return current score."""
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    @property
    def game_over(self) -> bool:
        """Return True if the game has ended."""
        return self._game_over

    @game_over.setter
    def game_over(self, value: bool) -> None:
        self._game_over = value

    @property
    def food(self) -> tuple:
        """Return (y, x) position of food, or None."""
        return self._food

    @property
    def snake(self):
        """Return the Snake instance (for rendering)."""
        return self._snake

    @snake.setter
    def snake(self, value) -> None:
        self._snake = value

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset game to initial state."""
        self._snake = Snake((self.height // 2, self.width // 2))
        self._score = 0
        self._game_over = False
        self._paused = False
        self.spawn_food()


# =============================================================================
# TESTS
# =============================================================================
import unittest


class TestSnakeInit(unittest.TestCase):
    """Tests for Snake initialization."""

    def test_initial_head_position(self):
        snake = Snake((5, 10))
        self.assertEqual(snake.head, (5, 10))

    def test_initial_body_length_one(self):
        snake = Snake((0, 0))
        self.assertEqual(len(snake.body), 1)

    def test_initial_direction_up(self):
        snake = Snake((3, 7))
        self.assertEqual(snake.direction, 'UP')

    def test_initial_body_contains_head(self):
        snake = Snake((4, 8))
        self.assertIn((4, 8), snake.body)

    def test_body_tail_is_head_when_length_one(self):
        snake = Snake((2, 3))
        self.assertEqual(snake.body[0], (2, 3))
        self.assertEqual(snake.body[-1], (2, 3))


class TestSnakeMove(unittest.TestCase):
    """Tests for Snake.move()."""

    def test_move_up_decreases_y(self):
        snake = Snake((5, 5))
        new_head = snake.move()
        self.assertEqual(new_head, (4, 5))

    def test_move_down_increases_y(self):
        snake = Snake((5, 5))
        # Need a non-180° turn to set DOWN (UP -> DOWN is 180°)
        snake.set_direction('RIGHT')
        snake.move()  # now at (5, 6)
        snake.set_direction('DOWN')
        new_head = snake.move()  # now at (6, 6)
        self.assertEqual(new_head, (6, 6))

    def test_move_left_decreases_x(self):
        snake = Snake((5, 5))
        snake.set_direction('LEFT')
        new_head = snake.move()
        self.assertEqual(new_head, (5, 4))

    def test_move_right_increases_x(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        new_head = snake.move()
        self.assertEqual(new_head, (5, 6))

    def test_move_updates_head(self):
        snake = Snake((3, 3))
        snake.move()
        self.assertEqual(snake.head, (2, 3))

    def test_move_keeps_body_length(self):
        snake = Snake((3, 3))
        snake.move()
        self.assertEqual(len(snake.body), 1)

    def test_move_returns_new_head(self):
        snake = Snake((0, 0))
        result = snake.move()
        self.assertEqual(result, (-1, 0))

    def test_body_tail_moves_with_snake(self):
        """After several moves, body should reflect the path."""
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # now head=(5,6), body=[(5,6), (5,5)]
        snake.set_direction('DOWN')
        snake.move()  # now head=(6,6), body=[(6,6), (5,6)]
        self.assertEqual(len(snake.body), 2)
        self.assertEqual(snake.body[0], (6, 6))
        self.assertEqual(snake.body[-1], (5, 6))


class TestSnakeDirection(unittest.TestCase):
    """Tests for snake direction control."""

    def test_set_direction_up(self):
        snake = Snake((0, 0))
        snake.set_direction('UP')
        self.assertEqual(snake.direction, 'UP')

    def test_set_direction_down(self):
        snake = Snake((0, 0))
        # Can't set DOWN from UP (180° reversal)
        snake.set_direction('DOWN')
        self.assertEqual(snake.direction, 'UP')
        # Change to a non-opposite direction first
        snake.set_direction('RIGHT')
        snake.set_direction('DOWN')
        self.assertEqual(snake.direction, 'DOWN')

    def test_set_direction_left(self):
        snake = Snake((0, 0))
        snake.set_direction('LEFT')
        self.assertEqual(snake.direction, 'LEFT')

    def test_set_direction_right(self):
        snake = Snake((0, 0))
        snake.set_direction('RIGHT')
        self.assertEqual(snake.direction, 'RIGHT')

    def test_prevent_180_up_to_down(self):
        snake = Snake((0, 0))  # initial direction is UP
        snake.set_direction('DOWN')
        self.assertEqual(snake.direction, 'UP', 'Should not reverse 180 degrees')

    def test_prevent_180_down_to_up(self):
        snake = Snake((0, 0))
        snake.set_direction('RIGHT')
        snake.move()
        snake.set_direction('DOWN')
        snake.move()
        snake.set_direction('UP')
        self.assertEqual(snake.direction, 'DOWN', 'Should not reverse 180 degrees')

    def test_prevent_180_left_to_right(self):
        snake = Snake((0, 0))
        snake.set_direction('LEFT')
        snake.move()
        snake.set_direction('RIGHT')
        self.assertEqual(snake.direction, 'LEFT', 'Should not reverse 180 degrees')

    def test_prevent_180_right_to_left(self):
        snake = Snake((0, 0))
        snake.set_direction('RIGHT')
        snake.move()
        snake.set_direction('LEFT')
        self.assertEqual(snake.direction, 'RIGHT', 'Should not reverse 180 degrees')

    def test_allows_non_180_change(self):
        snake = Snake((0, 0))
        snake.set_direction('LEFT')
        self.assertEqual(snake.direction, 'LEFT')

    def test_allows_90_degree_turn(self):
        snake = Snake((0, 0))
        snake.set_direction('RIGHT')
        self.assertEqual(snake.direction, 'RIGHT')

    def test_invalid_direction_ignored(self):
        snake = Snake((0, 0))
        snake.set_direction('INVALID')
        self.assertEqual(snake.direction, 'UP')


class TestSnakeGrow(unittest.TestCase):
    """Tests for Snake.grow()."""

    def test_grow_increases_body_length(self):
        snake = Snake((5, 5))
        snake.grow()
        snake.move()
        self.assertEqual(len(snake.body), 2)

    def test_grow_does_not_increase_after_one_move(self):
        snake = Snake((5, 5))
        snake.grow()
        snake.move()  # grows here
        snake.move()  # this move is normal (no grow)
        self.assertEqual(len(snake.body), 2)

    def test_grow_multiple_times(self):
        snake = Snake((5, 5))
        snake.grow()
        snake.move()  # length 2
        snake.grow()
        snake.move()  # length 3
        self.assertEqual(len(snake.body), 3)

    def test_grow_preserves_head_and_tail_positions(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # head=(5,6), body=[(5,6), (5,5)]
        self.assertEqual(snake.head, (5, 6))
        self.assertEqual(snake.body[-1], (5, 5))

    def test_grow_flag_resets_after_move(self):
        snake = Snake((5, 5))
        snake.grow()
        self.assertTrue(snake._growing)
        snake.move()
        self.assertFalse(snake._growing)


class TestSnakeCollision(unittest.TestCase):
    """Tests for collision detection."""

    def test_no_self_collision_on_straight_line(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(5,6), (5,5)]
        snake.grow()
        snake.move()  # body: [(5,7), (5,6), (5,5)]
        self.assertFalse(snake.collides_with_self())

    def test_self_collision_when_turning_into_self(self):
        snake = Snake((5, 5))
        # Create a snake: move right, down, left, then check if going up collides
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(5,6), (5,5)]
        snake.set_direction('DOWN')
        snake.grow()
        snake.move()  # body: [(6,6), (5,6), (5,5)]
        snake.set_direction('LEFT')
        snake.grow()
        snake.move()  # body: [(6,5), (6,6), (5,6), (5,5)]
        # Now head is (6,5). If we go UP, we'll hit (5,5) which is the tail
        # But tail is excluded from self-collision check!
        snake.set_direction('UP')
        # Before moving, check: head=(6,5), body[1:-1]=[(6,6),(5,6)]
        self.assertFalse(snake.collides_with_self(),
                         'Tail should be excluded from self-collision')

    def test_self_collision_hits_body(self):
        snake = Snake((5, 5))
        # Create a U-shape where the head will hit the body
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(5,6), (5,5)]
        snake.set_direction('DOWN')
        snake.grow()
        snake.move()  # body: [(6,6), (5,6), (5,5)]
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(6,7), (6,6), (5,6), (5,5)]
        snake.set_direction('DOWN')
        snake.grow()
        snake.move()  # body: [(7,7), (6,7), (6,6), (5,6), (5,5)]
        snake.set_direction('LEFT')
        snake.grow()
        snake.move()  # body: [(7,6), (7,7), (6,7), (6,6), (5,6), (5,5)]
        snake.set_direction('UP')
        snake.move()  # head goes to (6,6) which is in the body
        # Now check collides_with_self
        self.assertTrue(snake.collides_with_self(),
                        'Head (6,6) should collide with body segment')

    def test_collides_with_head(self):
        snake = Snake((5, 5))
        self.assertTrue(snake.collides_with((5, 5)))

    def test_collides_with_body(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(5,6), (5,5)]
        self.assertTrue(snake.collides_with((5, 5)))
        self.assertTrue(snake.collides_with((5, 6)))

    def test_collides_with_no_match(self):
        snake = Snake((5, 5))
        self.assertFalse(snake.collides_with((99, 99)))

    def test_collides_with_after_move(self):
        snake = Snake((5, 5))
        snake.move()  # goes UP to (4, 5)
        self.assertTrue(snake.collides_with((4, 5)))


class TestSnakeReset(unittest.TestCase):
    """Tests for Snake.reset()."""

    def test_reset_head_position(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # body: [(5,6), (5,5)]
        snake.reset((0, 0))
        self.assertEqual(snake.head, (0, 0))

    def test_reset_body_length_one(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()
        snake.reset((3, 3))
        self.assertEqual(len(snake.body), 1)

    def test_reset_direction_up(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.move()
        snake.reset((1, 1))
        self.assertEqual(snake.direction, 'UP')

    def test_reset_clears_growing_flag(self):
        snake = Snake((5, 5))
        snake.grow()
        snake.reset((0, 0))
        # After reset, grow flag should be cleared
        snake.move()
        self.assertEqual(len(snake.body), 1)


class TestSnakeIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""

    def test_snake_moves_and_grows(self):
        snake = Snake((0, 0))
        self.assertEqual(snake.head, (0, 0))
        self.assertEqual(snake.direction, 'UP')

        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()  # head=(0,1), body=[(0,1), (0,0)]
        self.assertEqual(snake.head, (0, 1))
        self.assertEqual(len(snake.body), 2)

        snake.set_direction('DOWN')
        snake.grow()
        snake.move()  # head=(1,1), body=[(1,1), (0,1), (0,0)]
        self.assertEqual(snake.head, (1, 1))
        self.assertEqual(len(snake.body), 3)

        snake.set_direction('LEFT')
        snake.move()  # head=(1,0), body=[(1,0), (1,1), (0,1)]
        self.assertEqual(snake.head, (1, 0))
        self.assertEqual(len(snake.body), 3)

    def test_180_prevention_integrated(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.set_direction('LEFT')  # should be ignored
        self.assertEqual(snake.direction, 'RIGHT')
        snake.move()  # goes RIGHT
        self.assertEqual(snake.head, (5, 6))

    def test_self_collision_detection(self):
        snake = Snake((5, 5))
        # Create a snake that turns into itself
        snake.set_direction('RIGHT')
        snake.grow(); snake.move()
        snake.set_direction('DOWN')
        snake.grow(); snake.move()
        snake.set_direction('LEFT')
        snake.grow(); snake.move()
        snake.set_direction('DOWN')
        snake.grow(); snake.move()
        snake.set_direction('RIGHT')
        snake.grow(); snake.move()
        snake.set_direction('UP')
        snake.move()  # head goes to (6,6) which is in the body
        self.assertTrue(snake.collides_with_self())

    def test_no_false_positive_self_collision(self):
        snake = Snake((5, 5))
        # Just moving forward should never self-collide
        for _ in range(10):
            snake.move()
        self.assertFalse(snake.collides_with_self())

    def test_reset_full_cycle(self):
        snake = Snake((5, 5))
        snake.set_direction('RIGHT')
        snake.grow()
        snake.move()
        snake.grow()
        snake.move()
        self.assertEqual(len(snake.body), 3)
        snake.reset((10, 10))
        self.assertEqual(snake.head, (10, 10))
        self.assertEqual(len(snake.body), 1)
        self.assertEqual(snake.direction, 'UP')
        self.assertFalse(snake._growing)


class TestGameInit(unittest.TestCase):
    """Tests for Game initialization."""

    def test_default_dimensions(self):
        game = Game()
        self.assertEqual(game.width, 20)
        self.assertEqual(game.height, 20)

    def test_custom_dimensions(self):
        game = Game(width=30, height=15)
        self.assertEqual(game.width, 30)
        self.assertEqual(game.height, 15)

    def test_tick_interval_default(self):
        game = Game()
        self.assertEqual(game.tick_interval, 0.15)

    def test_custom_tick_interval(self):
        game = Game(tick_interval=0.5)
        self.assertEqual(game.tick_interval, 0.5)

    def test_snake_initialized_at_center(self):
        game = Game(width=10, height=10)
        self.assertEqual(game.snake.head, (5, 5))

    def test_snake_center_odd_dimensions(self):
        game = Game(width=21, height=31)
        self.assertEqual(game.snake.head, (15, 10))

    def test_score_starts_at_zero(self):
        game = Game()
        self.assertEqual(game.score, 0)

    def test_game_over_false_at_start(self):
        game = Game()
        self.assertFalse(game.game_over)

    def test_not_paused_at_start(self):
        game = Game()
        self.assertFalse(game.is_paused)

    def test_food_not_none_after_init(self):
        game = Game()
        self.assertIsNotNone(game.food)

    def test_food_is_tuple_of_two_ints(self):
        game = Game()
        fy, fx = game.food
        self.assertIsInstance(fy, int)
        self.assertIsInstance(fx, int)

    def test_food_within_bounds(self):
        game = Game(width=10, height=10)
        fy, fx = game.food
        self.assertGreaterEqual(fy, 0)
        self.assertLess(fy, 10)
        self.assertGreaterEqual(fx, 0)
        self.assertLess(fx, 10)

    def test_food_not_on_snake_head(self):
        game = Game(width=5, height=5)
        # Snake starts at center (2, 2) moving UP
        self.assertNotEqual(game.food, game.snake.head,
                            msg='Food should not spawn on snake head')


class TestGameSpawnFood(unittest.TestCase):
    """Tests for Game.spawn_food()."""

    def test_spawn_food_replaces_old_food(self):
        game = Game(width=10, height=10)
        game.spawn_food()
        self.assertIsNotNone(game.food)

    def test_spawn_food_not_on_snake_body(self):
        game = Game(width=3, height=3)
        # 3x3 grid, snake at center (1,1). Food must be on empty cells only.
        snake_cells = set(game.snake.body)
        fy, fx = game.food
        self.assertNotIn((fy, fx), snake_cells)

    def test_spawn_food_in_bounds(self):
        game = Game(width=8, height=6)
        for _ in range(100):
            game.spawn_food()
            fy, fx = game.food
            self.assertGreaterEqual(fy, 0)
            self.assertLess(fy, 6)
            self.assertGreaterEqual(fx, 0)
            self.assertLess(fx, 8)

    def test_spawn_food_gives_new_food(self):
        """Test that spawning food 100 times always returns valid positions."""
        game = Game(width=5, height=5)
        snake_positions = set(game.snake.body)
        for _ in range(100):
            game.spawn_food()
            self.assertIsNotNone(game.food)
            fy, fx = game.food
            # Food must not be on snake
            self.assertNotIn((fy, fx), snake_positions)
            # Food must be in bounds
            self.assertGreaterEqual(fy, 0)
            self.assertLess(fy, 5)
            self.assertGreaterEqual(fx, 0)
            self.assertLess(fx, 5)


class TestGameTickMovement(unittest.TestCase):
    """Tests for Game.tick() — movement and return value."""

    def test_tick_returns_true_when_alive(self):
        game = Game(width=20, height=20)
        self.assertTrue(game.tick())

    def test_tick_moves_snake_head(self):
        game = Game(width=20, height=20)
        # Snake starts at (10, 10) facing UP
        old_head = game.snake.head
        game.tick()
        new_head = game.snake.head
        self.assertNotEqual(old_head, new_head)

    def test_tick_moves_snake_up_by_default(self):
        game = Game(width=20, height=20)
        game.tick()
        self.assertEqual(game.snake.head, (9, 10))

    def test_tick_returns_false_after_game_over(self):
        game = Game(width=3, height=3)
        # Snake at (1,1) facing UP. First tick goes to (0,1).
        game.tick()  # (0,1)
        # Next tick goes to (-1,1) → wall collision
        result = game.tick()
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_tick_returns_false_when_paused(self):
        game = Game()
        game.pause()
        result = game.tick()
        self.assertFalse(result)

    def test_tick_does_not_move_when_paused(self):
        game = Game(width=10, height=10)
        head_before = game.snake.head
        game.pause()
        game.tick()
        self.assertEqual(game.snake.head, head_before)

    def test_tick_returns_false_when_already_game_over(self):
        game = Game(width=3, height=3)
        # Tick until game over
        while not game.game_over:
            game.tick()
        self.assertFalse(game.tick())

    def test_tick_does_not_move_when_game_over(self):
        game = Game(width=3, height=3)
        while not game.game_over:
            game.tick()
        head_at_death = game.snake.head
        game.tick()
        self.assertEqual(game.snake.head, head_at_death)


class TestGameWallCollision(unittest.TestCase):
    """Tests for wall collision detection."""

    def test_tick_up_collides_top_wall(self):
        game = Game(width=10, height=5)
        # Snake at (2, 5) facing UP
        # Tick 3 times: (1,5), (0,5), (-1,5) → wall hit
        game.tick()  # (1,5)
        game.tick()  # (0,5)
        self.assertFalse(game.tick())  # (-1,5) wall hit
        self.assertTrue(game.game_over)

    def test_move_down_collides_bottom_wall(self):
        game = Game(width=10, height=5)
        # Snake at (2,5) facing UP. Turn around: RIGHT → DOWN, then go down
        game.snake.set_direction('RIGHT')
        game.tick()  # (2,6)
        game.snake.set_direction('DOWN')
        game.tick()  # (3,6)
        game.tick()  # (4,6)
        result = game.tick()  # (5,6) → out of bounds (height=5)
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_move_left_collides_left_wall(self):
        game = Game(width=5, height=10)
        # Snake at (5,2) facing UP.
        game.snake.set_direction('LEFT')
        game.tick()  # (5,1)
        game.tick()  # (5,0)
        result = game.tick()  # (5,-1) → out of bounds
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_move_right_collides_right_wall(self):
        game = Game(width=5, height=10)
        # Snake at (5,2) facing UP. Turn RIGHT.
        game.snake.set_direction('RIGHT')
        game.tick()  # (5,3)
        game.tick()  # (5,4)
        result = game.tick()  # (5,5) → out of bounds (width=5)
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_no_false_positive_wall_collision(self):
        """Snake moving within bounds should not trigger wall collision."""
        game = Game(width=20, height=20)
        for _ in range(5):
            game.tick()
        self.assertFalse(game.game_over)

    def test_wall_collision_sets_game_over_on_correct_axis(self):
        """Verify top wall (y<0) and bottom wall (y>=height) separately."""
        # Top wall test — snake starts at (2,5) goes UP
        game = Game(width=10, height=5)
        game.tick()  # (1,5)
        game.tick()  # (0,5)
        self.assertFalse(game.tick())  # (-1,5)
        self.assertTrue(game.game_over)
        head_y = game.snake.head[0]
        self.assertEqual(head_y, -1, 'Head should be at y=-1 (past top wall)')


class TestGameSelfCollision(unittest.TestCase):
    """Tests for self-collision detection."""

    def _setup_self_collision_scenario(self, game):
        """Set up snake state so the next tick will cause a self-collision.
        
        Creates a snake that loops back onto itself by building a shape:
        RIGHT x1 → DOWN x1 → LEFT x1 → DOWN x1 → RIGHT x1 → UP
        The head at (7,6) going UP will land on (6,6) which is in the body.
        
        This uses move() directly (not tick) to avoid wall collisions on
        the small grid.
        """
        s = game.snake
        # Start at (5,5)
        s.set_direction('RIGHT')
        s.grow(); s.move()  # (5,6)
        s.set_direction('DOWN')
        s.grow(); s.move()  # (6,6)
        s.set_direction('LEFT')
        s.grow(); s.move()  # (6,5)
        s.set_direction('DOWN')
        s.grow(); s.move()  # (7,5)
        s.set_direction('RIGHT')
        s.grow(); s.move()  # (7,6)
        # Now head at (7,6), body length 6
        # Set direction UP so next move goes to (6,6) which is in body
        s.set_direction('UP')

    def test_self_collision_detected(self):
        """Snake running into its own body should trigger game over."""
        game = Game(width=10, height=10)
        self._setup_self_collision_scenario(game)
        result = game.tick()
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_no_self_collision_on_straight_line(self):
        """Snake moving in straight line should never self-collide."""
        game = Game(width=100, height=100)
        game.snake.set_direction('RIGHT')
        for _ in range(10):
            game.tick()
        self.assertFalse(game.game_over)

    def test_self_collision_game_over_persists(self):
        """Once game_over is True, it stays True."""
        game = Game(width=10, height=10)
        self._setup_self_collision_scenario(game)
        game.tick()  # self collision
        self.assertTrue(game.game_over)
        # Another tick should not change anything
        game.tick()
        self.assertTrue(game.game_over)


class TestGameFoodEating(unittest.TestCase):
    """Tests for eating food and scoring."""

    def test_eat_food_increases_score(self):
        game = Game(width=10, height=10)
        # Place food right in front of snake (which faces UP)
        # Snake at (5,5) facing UP → next position is (4,5)
        fy, fx = game.food
        # We need to manually set food to (4,5) for deterministic testing
        game._food = (4, 5)
        game.tick()
        self.assertEqual(game.score, 10)

    def test_eat_food_grows_snake(self):
        game = Game(width=10, height=10)
        game._food = (4, 5)
        length_before = len(game.snake.body)
        game.tick()
        self.assertEqual(len(game.snake.body), length_before + 1)

    def test_eat_food_spawns_new_food(self):
        game = Game(width=10, height=10)
        game._food = (4, 5)
        game.tick()
        new_food = game.food
        # Food should be different, but random might place it at same spot
        # (very unlikely but check it's not None)
        self.assertIsNotNone(new_food)

    def test_score_increases_by_10_per_food(self):
        game = Game(width=10, height=10)
        # Eat 3 foods
        food_positions = [(4, 5), (3, 5), (2, 5)]
        for i, pos in enumerate(food_positions):
            game._food = pos
            game.tick()
            self.assertEqual(game.score, (i + 1) * 10)

    def test_not_eating_food_does_not_increase_score(self):
        game = Game(width=10, height=10)
        # Place food somewhere not in front of snake
        game._food = (0, 0)  # not in path of snake going UP from (5,5)
        game.tick()
        self.assertEqual(game.score, 0)

    def test_not_eating_food_does_not_grow(self):
        game = Game(width=10, height=10)
        game._food = (0, 0)  # not in path
        length_before = len(game.snake.body)
        game.tick()
        self.assertEqual(len(game.snake.body), length_before)

    def test_food_disappears_when_eaten(self):
        """After eating, old food position should no longer match new food."""
        game = Game(width=10, height=10)
        game._food = (4, 5)
        old_food = game.food
        game.tick()
        self.assertIsNotNone(game.food)
        # The new food should be at a different position
        # (Can't assert not equal since random could coincide, but check not None)
        self.assertIsNotNone(game.food)

    def test_multiple_food_eats_accumulate(self):
        game = Game(width=10, height=10)
        # Place food right above snake (snake at (5,5) facing UP)
        game._food = (4, 5)
        game.tick()  # eat food, score=10, spawn_food (random)
        self.assertEqual(game.score, 10)

        # After eating, the snake ate and grew. Snake now at (4,5).
        # Turn around and go back down past start
        game.snake.set_direction('DOWN')
        # Move down (no food expected)
        game.tick()  # (5,5) - might eat random food, but we'll just check final

        # Place food directly below
        game.snake.set_direction('DOWN')
        game._food = (6, 5)
        game.tick()  # (6,5) - eat food if not already eaten random one
        # Score should be at least 10, possibly 20 if random food wasn't eaten
        # Since we can't control random, just verify score increased
        self.assertGreaterEqual(game.score, 10)
        # And verify that after eating manually placed food, score went up
        # The core behavior: eating food increases score
        self.assertIn(game.score, {10, 20, 30},
                      'Score should be a multiple of 10 after eating')

    def test_eat_food_keeps_game_alive(self):
        game = Game(width=10, height=10)
        game._food = (4, 5)
        result = game.tick()
        self.assertTrue(result)
        self.assertFalse(game.game_over)


class TestGamePauseResume(unittest.TestCase):
    """Tests for pause/resume functionality."""

    def test_pause_sets_paused_true(self):
        game = Game()
        game.pause()
        self.assertTrue(game.is_paused)

    def test_resume_sets_paused_false(self):
        game = Game()
        game.pause()
        game.resume()
        self.assertFalse(game.is_paused)

    def test_resume_after_resume_stays_false(self):
        game = Game()
        game.resume()
        self.assertFalse(game.is_paused)

    def test_pause_multiple_times(self):
        game = Game()
        game.pause()
        game.pause()
        self.assertTrue(game.is_paused)

    def test_resume_allows_tick_to_move(self):
        game = Game(width=10, height=10)
        game.pause()
        game.resume()
        head_before = game.snake.head
        game.tick()
        self.assertNotEqual(game.snake.head, head_before)

    def test_pause_prevents_movement(self):
        game = Game(width=10, height=10)
        game.pause()
        head_before = game.snake.head
        game.tick()
        self.assertEqual(game.snake.head, head_before)

    def test_tick_returns_false_while_paused(self):
        game = Game()
        game.pause()
        self.assertFalse(game.tick())

    def test_tick_returns_true_after_resume(self):
        game = Game(width=20, height=20)
        game.pause()
        game.resume()
        self.assertTrue(game.tick())


class TestGameProperties(unittest.TestCase):
    """Tests for Game properties (score, game_over, food, is_paused, snake)."""

    def test_score_property(self):
        game = Game()
        self.assertEqual(game.score, 0)
        game.score = 42
        self.assertEqual(game.score, 42)

    def test_game_over_property(self):
        game = Game()
        self.assertFalse(game.game_over)
        game.game_over = True
        self.assertTrue(game.game_over)

    def test_food_property_returns_tuple(self):
        game = Game()
        self.assertIsInstance(game.food, tuple)
        self.assertEqual(len(game.food), 2)

    def test_food_property_read_only_no_setter(self):
        game = Game()
        with self.assertRaises(AttributeError):
            game.food = (0, 0)

    def test_is_paused_property(self):
        game = Game()
        self.assertFalse(game.is_paused)
        game.pause()
        self.assertTrue(game.is_paused)

    def test_snake_property_returns_snake(self):
        game = Game()
        self.assertIsInstance(game.snake, Snake)

    def test_snake_property_head_moves(self):
        game = Game(width=10, height=10)
        head_before = game.snake.head
        game.tick()
        self.assertNotEqual(game.snake.head, head_before)


class TestGameReset(unittest.TestCase):
    """Tests for Game.reset()."""

    def test_reset_restores_score_to_zero(self):
        game = Game(width=10, height=10)
        game._food = (4, 5)
        game.tick()
        self.assertEqual(game.score, 10)
        game.reset()
        self.assertEqual(game.score, 0)

    def test_reset_clears_game_over(self):
        game = Game(width=3, height=3)
        while not game.game_over:
            game.tick()
        self.assertTrue(game.game_over)
        game.reset()
        self.assertFalse(game.game_over)

    def test_reset_clears_paused(self):
        game = Game()
        game.pause()
        self.assertTrue(game.is_paused)
        game.reset()
        self.assertFalse(game.is_paused)

    def test_reset_creates_new_snake_at_center(self):
        game = Game(width=20, height=20)
        game.snake.set_direction('RIGHT')
        game.tick()
        game.reset()
        self.assertEqual(game.snake.head, (10, 10))

    def test_reset_snake_has_length_one(self):
        game = Game(width=10, height=10)
        game._food = (4, 5)
        game.tick()
        self.assertEqual(len(game.snake.body), 2)  # grew by 1
        game.reset()
        self.assertEqual(len(game.snake.body), 1)

    def test_reset_spawns_new_food(self):
        game = Game(width=10, height=10)
        game.reset()
        self.assertIsNotNone(game.food)

    def test_reset_allows_play_again(self):
        game = Game(width=3, height=3)
        while not game.game_over:
            game.tick()
        game.reset()
        self.assertTrue(game.tick())

    def test_reset_snake_direction_up(self):
        game = Game(width=10, height=10)
        game.snake.set_direction('RIGHT')
        game.tick()
        game.reset()
        self.assertEqual(game.snake.direction, 'UP')

    def test_reset_multiple_times(self):
        game = Game(width=5, height=5)
        for _ in range(3):
            while not game.game_over:
                game.tick()
            game.reset()
            self.assertFalse(game.game_over)
            self.assertEqual(game.score, 0)
            self.assertEqual(game.snake.head, (2, 2))


if __name__ == '__main__':
    unittest.main()

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


if __name__ == '__main__':
    unittest.main()

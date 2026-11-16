import random
import pygame


class Round:
    """Represents one reaction-time round."""

    WAITING = "waiting"
    GO = "go"
    RESULT = "result"
    FALSE_START = "false_start"

    def __init__(self, min_wait_ms=1000, max_wait_ms=3000):
        if min_wait_ms < 0:
            raise ValueError("min_wait_ms cannot be negative")
        if max_wait_ms < min_wait_ms:
            raise ValueError("max_wait_ms must be >= min_wait_ms")

        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms
        self.wait_delay_ms = random.randint(min_wait_ms, max_wait_ms)

        self.state = self.WAITING
        self.start_time = pygame.time.get_ticks()
        self.go_time = None
        self.reaction_ms = None
        self.false_start = False

    def update(self):
        """Advance the round state.

        Returns ``"go"`` exactly once when the green state begins.
        """
        if self.state != self.WAITING:
            return None

        now = pygame.time.get_ticks()
        if now - self.start_time >= self.wait_delay_ms:
            self.state = self.GO
            self.go_time = now
            return "go"

        return None

    def register_input(self):
        """Register one user action.

        Waiting-phase input is explicitly treated as a false start.
        Valid reaction time is measured only from ``go_time``.

        Returns:
            "false_start" for an early input,
            reaction time in milliseconds for a valid input,
            None when the round is already finished.
        """
        now = pygame.time.get_ticks()

        if self.state == self.WAITING:
            self.false_start = True
            self.reaction_ms = None
            self.state = self.FALSE_START
            return "false_start"

        if self.state != self.GO or self.go_time is None:
            return None

        self.reaction_ms = max(0, now - self.go_time)
        self.state = self.RESULT
        return self.reaction_ms

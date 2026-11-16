import math
import struct

import pygame

from .round import Round


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (190, 55, 55)
DARK_BLUE = (30, 50, 95)
YELLOW = (235, 200, 65)
LIGHT_GRAY = (220, 220, 220)


class GameEngine:
    """Controls the complete reaction-time game lifecycle."""

    MODES = {
        "Easy": {"min_wait_ms": 1500, "max_wait_ms": 3000},
        "Medium": {"min_wait_ms": 1000, "max_wait_ms": 2500},
        "Difficult": {"min_wait_ms": 500, "max_wait_ms": 1800},
    }

    MODE_KEYS = {
        pygame.K_1: "Easy",
        pygame.K_2: "Medium",
        pygame.K_3: "Difficult",
    }

    def __init__(self, width, height, rounds_total=5):
        if rounds_total <= 0:
            raise ValueError("rounds_total must be greater than 0")

        self.width = width
        self.height = height
        self.rounds_total = rounds_total

        self.result_pause_ms = 900
        self.round = None
        self.reaction_times = []
        self.false_starts = 0
        self.rounds_completed = 0
        self.result_shown_at = None
        self.current_mode = None
        self.game_over = False
        self.screen_state = "mode_select"
        self.previous_results = None

        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 52)
        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 32, bold=True)

        self.mode_buttons = self._build_mode_buttons()
        self.play_again_button = self._build_play_again_button()
        self.sounds_enabled = False
        self.go_sound = None
        self.false_start_sound = None
        self.session_end_sound = None
        self._init_sounds()

    def _build_mode_buttons(self):
        button_width = 220
        button_height = 65
        gap = 25
        total_width = button_width * 3 + gap * 2
        left = (self.width - total_width) // 2
        top = self.height // 2 - button_height // 2

        return {
            "Easy": pygame.Rect(left, top, button_width, button_height),
            "Medium": pygame.Rect(left + button_width + gap, top, button_width, button_height),
            "Difficult": pygame.Rect(
                left + (button_width + gap) * 2,
                top,
                button_width,
                button_height,
            ),
        }

    def _build_play_again_button(self):
        button_width = 250
        button_height = 70
        left = (self.width - button_width) // 2
        top = 470
        return pygame.Rect(left, top, button_width, button_height)

    def _init_sounds(self):
        """Create short PCM tones in memory; no external audio files are required."""
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

            sample_rate, sample_format, channels = pygame.mixer.get_init()
            if sample_format != -16 or channels != 1:
                # Reinitialize to the format used by _make_tone if another mixer
                # configuration was already active.
                pygame.mixer.quit()
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                sample_rate, sample_format, channels = pygame.mixer.get_init()

            self.go_sound = self._make_tone(
                [(880, 0.12, 0.55)], sample_rate, "go"
            )
            self.false_start_sound = self._make_tone(
                [(260, 0.14, 0.60), (180, 0.18, 0.60)], sample_rate, "false_start"
            )
            self.session_end_sound = self._make_tone(
                [(523, 0.10, 0.50), (659, 0.10, 0.50), (784, 0.18, 0.50)],
                sample_rate,
                "session_end",
            )
            self.sounds_enabled = True
        except pygame.error:
            # The game remains fully playable when audio hardware is unavailable.
            self.sounds_enabled = False
            self.go_sound = None
            self.false_start_sound = None
            self.session_end_sound = None

    @staticmethod
    def _make_tone(tones, sample_rate, _name):
        """Build a pygame Sound from one or more (frequency, duration, volume) tones."""
        frames = bytearray()
        max_amplitude = 32767

        for frequency, duration, volume in tones:
            sample_count = max(1, int(sample_rate * duration))
            for i in range(sample_count):
                envelope = 1.0
                fade_samples = max(1, int(sample_rate * 0.01))
                if i < fade_samples:
                    envelope = i / fade_samples
                elif i >= sample_count - fade_samples:
                    envelope = (sample_count - i) / fade_samples

                value = math.sin(2.0 * math.pi * frequency * i / sample_rate)
                sample = int(value * max_amplitude * volume * envelope)
                frames.extend(struct.pack("<h", sample))

        return pygame.mixer.Sound(buffer=bytes(frames))

    def _play_sound(self, sound):
        if self.sounds_enabled and sound is not None:
            sound.play()

    def _start_session(self, mode):
        settings = self.MODES[mode]
        self.current_mode = mode
        self.reaction_times = []
        self.false_starts = 0
        self.rounds_completed = 0
        self.result_shown_at = None
        self.game_over = False
        self.screen_state = "playing"
        self.round = Round(settings["min_wait_ms"], settings["max_wait_ms"])

    def _select_mode(self, mode):
        if mode not in self.MODES:
            return

        # The requested behavior is to print the previous session when the next
        # mode is selected. Do this before clearing the previous session data.
        if self.previous_results is not None:
            self._print_previous_results()

        self._start_session(mode)

    def _print_previous_results(self):
        previous = self.previous_results
        print("\n========== PREVIOUS SESSION ==========")
        print("Mode:", previous["mode"])
        print("Reaction times (ms):", previous["reaction_times"])
        print("False starts:", previous["false_starts"])
        print("Average:", previous["average_ms"], "ms")
        print("Best:", previous["best_ms"], "ms")
        print("======================================\n")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
            return

        if self.screen_state == "mode_select":
            self._handle_mode_selection_event(event)
            return

        if self.screen_state == "results":
            self._handle_results_event(event)
            return

        if self.screen_state != "playing":
            return

        is_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        is_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE

        if not (is_click or is_space):
            return

        # Input is allowed during both waiting and go so that an early press
        # can be explicitly flagged as a false start. It is ignored after the
        # round already has a result.
        if self.round.state in (Round.WAITING, Round.GO):
            result = self.round.register_input()

            if result == "false_start":
                self.false_starts += 1
                self.rounds_completed += 1
                self.result_shown_at = pygame.time.get_ticks()
                self._play_sound(self.false_start_sound)
            elif isinstance(result, int):
                self.reaction_times.append(result)
                self.rounds_completed += 1
                self.result_shown_at = pygame.time.get_ticks()

    def _handle_mode_selection_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in self.MODE_KEYS:
            self._select_mode(self.MODE_KEYS[event.key])
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for mode, rect in self.mode_buttons.items():
                if rect.collidepoint(event.pos):
                    self._select_mode(mode)
                    return

    def _handle_results_event(self, event):
        """Handle input on the final results screen.

        The result screen intentionally has only one action: Play Again.
        Selecting a difficulty happens on the separate mode-selection screen.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_again_button.collidepoint(event.pos):
                self.screen_state = "mode_select"
                return

        # Keyboard convenience: Enter/Space also moves to mode selection.
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.screen_state = "mode_select"

    def handle_input(self):
        """Reserved for continuously-held input; reaction input is event-based."""
        pass

    def update(self):
        if self.screen_state != "playing" or self.round is None:
            return

        transition = self.round.update()
        if transition == "go":
            self._play_sound(self.go_sound)

        if self.round.state in (Round.RESULT, Round.FALSE_START):
            if self.result_shown_at is None:
                self.result_shown_at = pygame.time.get_ticks()

            now = pygame.time.get_ticks()
            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_next_round(self):
        if self.rounds_completed >= self.rounds_total:
            self._finish_session()
            return

        settings = self.MODES[self.current_mode]
        self.round = Round(settings["min_wait_ms"], settings["max_wait_ms"])
        self.result_shown_at = None

    def _finish_session(self):
        self.game_over = True
        self.screen_state = "results"
        self.previous_results = {
            "mode": self.current_mode,
            "reaction_times": list(self.reaction_times),
            "false_starts": self.false_starts,
            "average_ms": self.average_reaction_ms(),
            "best_ms": self.best_reaction_ms(),
        }
        self._play_sound(self.session_end_sound)

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return round(sum(self.reaction_times) / len(self.reaction_times))

    def best_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return min(self.reaction_times)

    def worst_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return max(self.reaction_times)

    def _draw_centered(self, screen, text, font, y, color=WHITE):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.width // 2, y))
        screen.blit(surface, rect)

    def _draw_button(self, screen, mode, color):
        rect = self.mode_buttons[mode]
        pygame.draw.rect(screen, color, rect, border_radius=10)
        label = self.button_font.render(mode, True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def _draw_play_again_button(self, screen):
        rect = self.play_again_button
        pygame.draw.rect(screen, GREEN, rect, border_radius=10)
        label = self.button_font.render("PLAY AGAIN", True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def _render_mode_select(self, screen):
        screen.fill(DARK_BLUE)
        self._draw_centered(screen, "Reaction Time Tester", self.title_font, 120)
        self._draw_centered(
            screen,
            "Choose a difficulty to start",
            self.font,
            205,
            LIGHT_GRAY,
        )

        self._draw_button(screen, "Easy", GREEN)
        self._draw_button(screen, "Medium", BLUE)
        self._draw_button(screen, "Difficult", RED)

        self._draw_centered(
            screen,
            "Press 1 = Easy   2 = Medium   3 = Difficult",
            self.small_font,
            420,
            YELLOW,
        )

    def _render_playing(self, screen):
        if self.round.state == Round.WAITING:
            bg = GRAY
            message = "WAIT..."
            message_color = WHITE
        elif self.round.state == Round.GO:
            bg = GREEN
            message = "GO! CLICK NOW!"
            message_color = WHITE
        elif self.round.state == Round.FALSE_START:
            bg = RED
            message = "FALSE START!"
            message_color = WHITE
        else:
            bg = BLUE
            message = f"{self.round.reaction_ms} ms"
            message_color = WHITE

        screen.fill(bg)
        self._draw_centered(screen, message, self.big_font, self.height // 2, message_color)

        round_number = min(self.rounds_completed + 1, self.rounds_total)
        round_text = self.font.render(
            f"Round {round_number}/{self.rounds_total}", True, WHITE
        )
        screen.blit(round_text, (20, 20))

        avg_text = self.font.render(
            f"Avg: {self.average_reaction_ms()} ms", True, WHITE
        )
        avg_rect = avg_text.get_rect(topright=(self.width - 20, 20))
        screen.blit(avg_text, avg_rect)

        mode_text = self.small_font.render(
            f"Mode: {self.current_mode}", True, WHITE
        )
        screen.blit(mode_text, (20, self.height - 45))

    def _render_results(self, screen):
        screen.fill(DARK_BLUE)

        self._draw_centered(screen, "SESSION COMPLETE", self.title_font, 75, YELLOW)
        self._draw_centered(
            screen,
            f"Mode: {self.current_mode}",
            self.font,
            135,
            WHITE,
        )

        lines = [
            f"Valid reactions: {len(self.reaction_times)}/{self.rounds_total}",
            f"False starts: {self.false_starts}",
            f"Average: {self.average_reaction_ms()} ms",
            f"Best: {self.best_reaction_ms()} ms",
            f"Slowest: {self.worst_reaction_ms()} ms",
            f"Times: {self.reaction_times if self.reaction_times else 'None'}",
        ]

        y = 195
        for line in lines:
            self._draw_centered(screen, line, self.small_font, y, LIGHT_GRAY)
            y += 42

        self._draw_play_again_button(screen)

        self._draw_centered(
            screen,
            "Click PLAY AGAIN or press Enter / Space",
            self.small_font,
            565,
            YELLOW,
        )

    def render(self, screen):
        if self.screen_state == "mode_select":
            self._render_mode_select(screen)
        elif self.screen_state == "playing":
            self._render_playing(screen)
        elif self.screen_state == "results":
            self._render_results(screen)

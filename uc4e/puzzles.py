"""Puzzle objects for the UC4E tutorial level."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, List, Sequence

import pygame

from . import config


class Puzzle:
    """Base class for interactive puzzles."""

    name: str

    def update(self, dt: float) -> None:  # pragma: no cover - default no-op
        return

    def draw(self, surface: pygame.Surface) -> None:  # pragma: no cover
        return

    def interact(self, player: "Player") -> None:  # pragma: no cover
        return

    @property
    def solved(self) -> bool:
        raise NotImplementedError


@dataclass
class ToggleTerminal:
    position: pygame.Vector2
    on_color: pygame.Color
    off_color: pygame.Color
    active: bool = False
    radius: int = 20
    callback: Callable[[bool], None] | None = None

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.position.x - 24), int(self.position.y - 24), 48, 48)

    def toggle(self) -> None:
        self.active = not self.active
        if self.callback:
            self.callback(self.active)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface,
            self.on_color if self.active else self.off_color,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )
        pygame.draw.circle(
            surface,
            config.COLOR_HOLOGRAM,
            (int(self.position.x), int(self.position.y)),
            self.radius + 6,
            width=2,
        )


@dataclass
class Door:
    rect: pygame.Rect
    color: pygame.Color
    ghost: bool = False
    open_state: bool = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.open_state:
            return
        draw_color = self.color
        if self.ghost:
            draw_color = pygame.Color(self.color)
            draw_color = self.color.copy()
            draw_color.a = 120
        pygame.draw.rect(surface, draw_color, self.rect)


class SuperpositionPuzzle(Puzzle):
    name = "Superposition Bay"

    def __init__(self, detector: ToggleTerminal, doors: Sequence[Door]):
        self.detector = detector
        self.detector.callback = self._on_detector
        self.doors = list(doors)
        self._collapsed: bool = False
        self._chosen_index: int | None = None

    @property
    def solved(self) -> bool:
        return self._collapsed and self._chosen_index is not None and self.doors[self._chosen_index].open_state

    def _on_detector(self, active: bool) -> None:
        if active and not self._collapsed:
            self._collapsed = True
            self._chosen_index = random.randint(0, len(self.doors) - 1)
            for idx, door in enumerate(self.doors):
                door.open_state = idx == self._chosen_index
                door.ghost = False
        elif not active and self._collapsed:
            # Allow resetting to demonstrate repeated measurement influence
            self._collapsed = False
            self._chosen_index = None
            for door in self.doors:
                door.open_state = False
                door.ghost = True

    def draw(self, surface: pygame.Surface) -> None:
        for door in self.doors:
            door.draw(surface)
        self.detector.draw(surface)


class EntanglementPuzzle(Puzzle):
    name = "Entanglement Hall"

    def __init__(self, switches: Sequence[ToggleTerminal], doors: Sequence[Door]):
        if len(switches) != 2:
            raise ValueError("Entanglement puzzle requires exactly two switches")
        self.switches = list(switches)
        self.doors = list(doors)
        for switch in self.switches:
            switch.callback = self._on_switch
        self._state = False

    @property
    def solved(self) -> bool:
        return self._state and all(door.open_state for door in self.doors)

    def _on_switch(self, _: bool) -> None:
        self._state = not self._state
        for door in self.doors:
            door.open_state = self._state

    def draw(self, surface: pygame.Surface) -> None:
        for door in self.doors:
            door.draw(surface)
        for switch in self.switches:
            switch.draw(surface)


class Slider:
    def __init__(self, position: pygame.Vector2, label_color: pygame.Color, min_value: float = 0.0, max_value: float = 1.0):
        self.position = position
        self.value = 0.5
        self.min_value = min_value
        self.max_value = max_value
        self.label_color = label_color
        self.width = 200
        self.height = 12

    def adjust(self, delta: float) -> None:
        self.value = max(self.min_value, min(self.max_value, self.value + delta))

    def draw(self, surface: pygame.Surface) -> None:
        bar_rect = pygame.Rect(int(self.position.x - self.width / 2), int(self.position.y - self.height / 2), self.width, self.height)
        pygame.draw.rect(surface, config.COLOR_FLOOR_ACCENT, bar_rect)
        knob_x = bar_rect.left + int(self.value * bar_rect.width)
        knob_rect = pygame.Rect(knob_x - 8, bar_rect.centery - 16, 16, 32)
        pygame.draw.rect(surface, self.label_color, knob_rect, border_radius=4)
        pygame.draw.rect(surface, config.COLOR_HOLOGRAM, bar_rect, width=2, border_radius=4)


class UncertaintyPuzzle(Puzzle):
    name = "Uncertainty Workshop"

    def __init__(self, slider_position: Slider, slider_momentum: Slider):
        self.slider_position = slider_position
        self.slider_momentum = slider_momentum

    @property
    def solved(self) -> bool:
        return self.slider_position.value <= 0.35 and self.slider_momentum.value >= 0.65

    def adjust(self, position_delta: float, momentum_delta: float) -> None:
        self.slider_position.adjust(position_delta)
        self.slider_momentum.adjust(momentum_delta)

    def draw(self, surface: pygame.Surface) -> None:
        self.slider_position.draw(surface)
        self.slider_momentum.draw(surface)


class TunnelingPuzzle(Puzzle):
    name = "Tunneling Corridor"

    def __init__(self, energy_slider: Slider, gate: Door, barrier_width: float = 1.5, target_energy: float = 0.68):
        self.energy_slider = energy_slider
        self.gate = gate
        self.barrier_width = barrier_width
        self.target_energy = target_energy
        self.last_probability: float = 0.0

    @property
    def solved(self) -> bool:
        return self.gate.open_state

    def tune_energy(self, delta: float) -> None:
        self.energy_slider.adjust(delta)
        self._update_probability()

    def attempt_tunnel(self) -> bool:
        self._update_probability()
        chance = random.random()
        if chance <= self.last_probability:
            self.gate.open_state = True
            return True
        return False

    def _update_probability(self) -> None:
        mismatch = self.energy_slider.value - self.target_energy
        self.last_probability = math.exp(-self.barrier_width * (mismatch ** 2))

    def draw(self, surface: pygame.Surface) -> None:
        self.energy_slider.draw(surface)
        if not self.gate.open_state:
            self.gate.draw(surface)
        else:
            pygame.draw.rect(surface, config.COLOR_ACCENT_GREEN, self.gate.rect, width=3)

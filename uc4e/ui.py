"""UI widgets for dialogues and HUD."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

import pygame

from . import config


@dataclass
class DialogueLine:
    speaker: str
    text: str


@dataclass
class DialogueBox:
    """Timed dialogue box that can queue multiple lines."""

    font: pygame.font.Font
    queue: List[DialogueLine] = field(default_factory=list)
    current_timer: float = 0.0
    active_line: DialogueLine | None = None

    def add_lines(self, lines: Iterable[DialogueLine]) -> None:
        self.queue.extend(lines)
        if self.active_line is None and self.queue:
            self._advance()

    def update(self, dt: float) -> None:
        if self.active_line is None:
            return
        self.current_timer -= dt
        if self.current_timer <= 0:
            self._advance()

    def _advance(self) -> None:
        if self.queue:
            self.active_line = self.queue.pop(0)
            self.current_timer = config.DIALOGUE_LINE_DURATION
        else:
            self.active_line = None

    def draw(self, surface: pygame.Surface) -> None:
        if self.active_line is None:
            return
        margin = 24
        box_rect = pygame.Rect(
            margin,
            surface.get_height() - 180,
            surface.get_width() - margin * 2,
            160,
        )
        dialogue_surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        dialogue_surface.fill(config.COLOR_DIALOGUE_BG)

        speaker_text = self.font.render(self.active_line.speaker, True, config.COLOR_HOLOGRAM)
        body_wrapped = wrap_text(self.active_line.text, self.font, box_rect.width - 40)
        dialogue_surface.blit(speaker_text, (20, 12))
        for idx, line in enumerate(body_wrapped):
            rendered = self.font.render(line, True, config.COLOR_TEXT)
            dialogue_surface.blit(rendered, (20, 48 + idx * 28))

        surface.blit(dialogue_surface, box_rect)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

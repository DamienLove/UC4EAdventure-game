"""Player character definitions and controls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

import pygame

from . import config


@dataclass
class Player:
    """Represents one controllable scientist."""

    name: str
    position: pygame.Vector2
    color: pygame.Color
    facing: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 1))

    SIZE: Tuple[int, int] = (36, 48)

    def rect(self) -> pygame.Rect:
        half_w, half_h = self.SIZE[0] / 2, self.SIZE[1] / 2
        return pygame.Rect(
            int(self.position.x - half_w),
            int(self.position.y - half_h),
            int(self.SIZE[0]),
            int(self.SIZE[1]),
        )

    def update(self, dt: float, walls: Tuple[pygame.Rect, ...]) -> None:
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x += 1

        if velocity.length_squared() > 0:
            velocity = velocity.normalize() * config.PLAYER_SPEED
            self.facing = velocity.normalize()
        movement = velocity * dt
        if movement.length_squared() == 0:
            return

        # Axis-aligned collision resolution
        self._move_axis(movement.x, 0, walls)
        self._move_axis(0, movement.y, walls)

    def _move_axis(self, dx: float, dy: float, walls: Tuple[pygame.Rect, ...]) -> None:
        if dx == 0 and dy == 0:
            return
        rect = self.rect()
        rect.x += int(dx)
        rect.y += int(dy)
        for wall in walls:
            if rect.colliderect(wall):
                if dx > 0:
                    rect.right = wall.left
                if dx < 0:
                    rect.left = wall.right
                if dy > 0:
                    rect.bottom = wall.top
                if dy < 0:
                    rect.top = wall.bottom
        self.position.update(rect.center)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect()
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        # Add a small triangle to show facing direction
        tip = pygame.Vector2(rect.center) + self.facing * 18
        base_left = pygame.Vector2(rect.center) + self.facing.rotate(140) * 12
        base_right = pygame.Vector2(rect.center) + self.facing.rotate(-140) * 12
        pygame.draw.polygon(
            surface,
            config.COLOR_HOLOGRAM,
            [tip, base_left, base_right],
        )

"""
SakuyaEngine (c) 2020-2021 Andrew Hong
This code is licensed under MIT license (see LICENSE for details)
"""
from .physics import gravity
from typing import Tuple, List

import random
import math
import pygame

class Particle:
    def __init__(
        self,
        position: pygame.math.Vector2,
        color: Tuple[int, int, int],
        velocity: pygame.math.Vector2
    ):
        self.position = position
        self.color = color
        self.velocity = velocity
        self._destroy_val = 0
        self._enable_destroy = False
        self._is_destroyed = False
        
    def destroy(self, time: int) -> None:
        """
        :param int time: milliseconds to destruction
        """
        self._enable_destroy = True
        self._destroy_val = time + pygame.time.get_ticks()

    def update(self, delta_time: float) -> None:
        if self._enable_destroy and self._destroy_val <= pygame.time.get_ticks():
            self._is_destroyed = True

        self.velocity += gravity
        self.position += self.velocity * delta_time

class Particles:
    def __init__(
        self,
        velocity: pygame.math.Vector2,
        spread: int = 3,
        particles_num: int = 2,
        colors: List[Tuple[int, int, int]] = [],
        lifetime: int = 1000,
        offset: pygame.math.Vector2 = pygame.math.Vector2(0, 0),
        position: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
    ):
        self.particles = []
        self.velocity = velocity
        self.colors = colors
        self.spread = spread # pygame.math.Vector2
        self.particles_num = particles_num # int
        self.lifetime = lifetime
        self.offset = offset
        self.position = position
    
    def render(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            surface.set_at((int(p.position.x), int(p.position.y)), p.color)

    def update(self, delta_time: float) -> None:
        for p in range(self.particles_num):
            random_color = random.randrange(0, len(self.colors))
            random_spread_x = random.uniform(-self.spread, self.spread)
            random_spread_y = random.uniform(-self.spread, self.spread)
            par = Particle(
                self.position + self.offset,
                self.colors[random_color],
                pygame.math.Vector2(self.velocity.x + random_spread_x, self.velocity.y + random_spread_y)
            )
            par.destroy(self.lifetime)
            self.particles.append(par)

        for p in self.particles:
            if p._is_destroyed:
                self.particles.remove(p)
            p.update(delta_time)
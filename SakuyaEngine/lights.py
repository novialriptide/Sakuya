"""
SakuyaEngine (c) 2020-2021 Andrew Hong
This code is licensed under GNU LESSER GENERAL PUBLIC LICENSE (see LICENSE for details)
"""
from copy import copy
from .math import get_angle
from .scene import Scene
from .draw import draw_pie

import pygame
import math


class LightRoom:
    def __init__(self, scene: Scene, size: pygame.Vector2 = None):
        if size is None:
            self._screen = scene.screen.copy().convert_alpha()
        else:
            self._screen = pygame.Surface(size)
        
        self._screen.fill((0, 0, 0))

        self._crop_color = (0, 0, 0)
        self._outer_color = (0, 0, 100)
        self._mid_color = (0, 0, 175)
        self._inner_color = (0, 0, 255)

        self.outer_light_surfs = []
        self.inner_light_surfs = []
        self.outer_shadow_points = []

        self.alpha = 1

    @property
    def surface(self) -> pygame.Surface:
        self._screen.fill((0, 0, 0))
        for out_surf in self.outer_light_surfs:
            out_surf_keys = out_surf.keys()
            if "surf" in out_surf_keys:
                self._screen.blit(out_surf["surf"], out_surf["position"])

            elif "func" in out_surf_keys:
                out_surf["func"]()

        for in_surf in self.inner_light_surfs:
            in_surf_keys = in_surf.keys()
            if "surf" in in_surf_keys:
                self._screen.blit(in_surf["surf"], in_surf["position"])

            elif "func" in in_surf_keys:
                in_surf["func"]()

        for points in self.outer_shadow_points:
            pygame.draw.polygon(self._screen, self._crop_color, points)

        screen_array = pygame.PixelArray(self._screen)  # lgtm [py/call/wrong-arguments]
        screen_array.replace(self._outer_color, (0, 0, 0, 50))
        screen_array.replace(self._inner_color, (0, 0, 0, 0))

        self.outer_light_surfs = []
        self.inner_light_surfs = []
        self.outer_shadow_points = []

        self._screen.set_alpha(self.alpha * 255)
        return self._screen

    def draw_spot_light(
        self,
        position: pygame.Vector2,
        length: int,
        direction: int,
        spread: int,
        collisions=[],
    ) -> None:
        """Draws a spotlight.

        Parameters:
            position: Position of the spotlight.
            length: Length of the spotlight.
            direction: Direction of the spotlight in degrees.
            spread: Angle width of the spotlight in degrees.

        """
        start_angle = int(direction - spread / 2)
        end_angle = int(direction + spread / 2)

        outer_surf = pygame.Surface((length * 2, length * 2))
        draw_pie(
            outer_surf,
            self._outer_color,
            (length, length),
            length,
            start_angle,
            end_angle,
        )
        self.outer_light_surfs.append(
            {"surf": outer_surf, "position": position - pygame.Vector2(length, length)}
        )
        outer_surf.set_colorkey((0, 0, 0))

        inner_surf = pygame.Surface((length * 2, length * 2))
        draw_pie(
            inner_surf,
            self._inner_color,
            (length, length),
            int(length / 2),
            start_angle,
            end_angle,
        )
        self.inner_light_surfs.append(
            {"surf": inner_surf, "position": position - pygame.Vector2(length, length)}
        )
        inner_surf.set_colorkey((0, 0, 0))

        for line in collisions:
            points = list(copy(line))
            angle1 = get_angle(position, line[0])
            angle2 = get_angle(position, line[1])

            point1 = (
                int(length * 2 * math.cos(angle1)),
                int(length * 2 * math.sin(angle1)),
            )
            point2 = (
                int(length * 2 * math.cos(angle2)),
                int(length * 2 * math.sin(angle2)),
            )

            points.append(pygame.Vector2(line[1]) + point2)
            points.append(pygame.Vector2(line[0]) + point1)

            self.outer_shadow_points.append(points)

    def draw_point_light(
        self,
        position: pygame.Vector2,
        radius: int,
        collisions=[],
    ) -> None:
        self.draw_spot_light(position, radius, 0, 360, collisions=collisions)

    def draw_area_light(
        self,
        position1: pygame.Vector2,
        position2: pygame.Vector2,
        length: int,
        direction: float,
    ) -> None:
        # TODO: Make this work with collisions

        direction = math.radians(direction)
        position_offset1 = pygame.Vector2(
            length * math.cos(direction), length * math.sin(direction)
        )
        points1 = [
            position1,
            position2,
            position2 + position_offset1,
            position1 + position_offset1,
        ]

        def draw_outer_surf():
            pygame.draw.polygon(self._screen, self._outer_color, points1)

        self.outer_light_surfs.append({"func": draw_outer_surf, "position": None})

        position_offset2 = pygame.Vector2(
            length / 2 * math.cos(direction), length / 2 * math.sin(direction)
        )
        points2 = [
            position1,
            position2,
            position2 + position_offset2,
            position1 + position_offset2,
        ]

        def draw_inner_surf():
            pygame.draw.polygon(self._screen, self._inner_color, points2)

        self.inner_light_surfs.append({"func": draw_inner_surf, "position": None})

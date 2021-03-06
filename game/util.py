from colorsys import rgb_to_hsv, hsv_to_rgb
import random
from functools import lru_cache
from typing import Union, Optional

import glm  # for mix (conflicts with util.mix)
from glm import vec3, vec4, ivec2, ivec3, ivec4, normalize, cross, dot, vec2

from game.constants import EPSILON, DEBUG
import pygame


def map_range(val, r1, r2):
    return (val - r1[0]) / (r1[1] - r1[0]) * (r2[1] - r2[0]) + r2[0]


def clamp(x, mini=0, maxi=1):
    if mini > maxi:
        return x
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def surf_fader(max_dist, dz):
    """
    Get alpha value for fade.
    
    Arguments:
        max_dist {int} -- Maximum distance until butterflies disappear completely
        dz {int} -- Difference of Z pos between camera and butterfly
    """

    return clamp((max_dist - dz) / max_dist * 255, 0, 255)


def rgb2hsv(r, g, b):
    """Conversion between rgb in range 0-255 to hsv"""
    return rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv2rgb(h, s, v):
    """Conversion between hsv to rgb in range 0-255"""
    s = clamp(s)
    v = clamp(v)

    r, g, b = hsv_to_rgb(h % 1, s, v)
    return (
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )


def random_color():
    """Random RGB color of the rainbow"""
    return hsv2rgb(random.random(), 1, 1)


def plane_intersection(p1: vec3, d1: vec3, p2: vec3, d2: vec3):
    """
    Compute the line of intersection of the two planes.

    Note: if the two planes are parallel or equal this returns None.

    :param p1: a point in the first plane
    :param d1: a vector normal to the first plane
    :param p2: a point in the second plane
    :param d2: a normal vector of the second plane
    :return: None if they are parallel else (p3, d3)
        where p3 is a point in the line of intersection
        and d3 is the direction of this line
    """

    d1 = normalize(d1)
    d2 = normalize(d2)

    if d1 in (d2, -d2):
        # planes are parallel
        return None

    d3 = cross(d1, d2)

    # d3 and v1 are an orthonormal base of the first plane
    v1 = cross(d3, d1)
    b = -dot(p1, d2) / dot(v1, d2)

    p3 = p1 + b * v1
    return p3, d3


def cross2d(a, b):
    return a.x * b.y - a.y * b.x


def line_intersection(p, u, q, v) -> Optional[vec2]:
    """
    Compute the intersection of two 2d lines.

    :param p: a point on the first line
    :param u: direction of the first line
    :param q: a point on the first line
    :param v: direction of the first line
    :return: None if no intersection
    """

    cross = cross2d(u, v)
    if abs(cross) < EPSILON:
        return None

    w = p - q
    s = cross2d(u, w) / cross
    return p + s * u


def line_segment_intersection(a, b, p, u) -> Optional[vec2]:
    """
    Compute the intersection between a 2d line and a segment.

    :param a: start point of the segment
    :param b: end point of the segment
    :param p: a point of the line
    :param u: the direction of the line
    :return:
    """

    v = b - a
    cross = cross2d(v, u)
    if abs(cross) < EPSILON:
        return None

    w = a - p
    s = cross2d(v, w) / cross
    if 0 <= s <= 1:
        return a + s * v
    return None


def estimate_3d_size(size_2d):
    """
    Return a 3D size given a sprite size.
    Last coordinate is set to the minimum dimension of the two first.
    """

    return vec3(*size_2d, min(size_2d))


def pg_color(c):
    tc = type(c)
    if tc == pygame.Color:
        return c
    elif tc == vec3:
        c = vec4(c, 0)
    elif tc == ivec3:
        c = vec4(c, 0)
    elif tc == ivec4:
        c = vec4(c, 0)
    elif tc == tuple:
        return c
    elif tc == str:
        return pygame.Color(c)
    c = tuple(int(clamp(x * 255, 0, 255)) for x in c)
    return c


def ncolor(c):
    """
    Normalize color based on type.
    Given a color string, a pygame color, or vec3,
    return that as a normalized vec4 color
    """
    tc = type(c)
    if tc == str:
        c = vec4(*pygame.Color(c)) / 255.0
    elif tc == tuple:
        c = vec4(*c, 0) / 255.0
    elif tc == c or tc == pygame.Color:
        c = vec4(*c) / 255.0
    elif tc == vec3:
        c = vec4(*c, 0)
    elif tc == float or tc == int:
        c = vec4(c, c, c, 0)
    elif c is None:
        c = vec4(0)
    return c


def rgb_mix(a, b, t):
    if t >= 1:
        return b
    if t <= 0:
        return a

    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )


def nrand(s=1.0):
    """
    normalized random scalar, scaled by S
    """
    return (random.random() * 2 - 1) * s


def mix(a, b, t):
    """
    interpolate a -> b @ t
    Returns a vec4
    Supports color names and pygame colors
    """
    if isinstance(a, vec3):
        return glm.mix(a, b, t)

    # this works for vec4 as well
    return glm.mix(ncolor(a), ncolor(b), t)


def random_vec3(s=1):
    return glm.normalize(vec3(nrand(), nrand(), nrand())) * s


def random_rgb():
    return vec4(random.random(), random.random(), random.random(), 0)


def random_char():
    """
    Random human-readable char
    """
    return chr(random.randint(32, 126))


def rand_RGB():
    return (
        random.randrange(255),
        random.randrange(255),
        random.randrange(255),
    )


@lru_cache(15)
def noise_surf(size, num=0):
    surf = pygame.Surface(size)
    for y in range(size[1]):
        for x in range(size[0]):
            surf.set_at((x, y), rand_RGB())
    surf.set_alpha(12)
    return surf


@lru_cache(15)
def noise_surf_dense_bottom(size, num=0):
    surf = pygame.Surface(size).convert_alpha()
    for y in range(size[1]):
        interp = 1 - y / size[1]
        alpha = min(int(0.02 / interp * 255), 255)
        for x in range(size[0]):
            surf.set_at(
                (x, y),
                (
                    min(random.randrange(10, 255) / interp / 6, 255),
                    min(random.randrange(10, 255) / interp / 6, 255),
                    min(random.randrange(10, 255) / interp / 6, 255),
                    alpha,
                ),
            )
    return surf


def debug_log_call(f: "function"):
    if DEBUG:

        def wrapper(*args, **kwargs):
            ar = [str(a) for a in args]
            kw = ["{n}={v}" for n, v in kwargs.items()]
            print(f"CALL {f.__name__}({', '.join(ar + kw)})")
            return f(*args, **kwargs)

        return wrapper

    return f

import pytest
from app.services.visual_inspector import (
    hex_to_rgb,
    rgb_to_hex,
    color_distance,
    calculate_contrast_ratio
)

def test_hex_rgb_conversions():
    rgb = hex_to_rgb("#1E3A8A")
    assert rgb == (30, 58, 138)
    assert rgb_to_hex(30, 58, 138).upper() == "#1E3A8A"

def test_color_distance():
    c1 = (0, 0, 0)
    c2 = (0, 0, 0)
    assert color_distance(c1, c2) == 0.0

    c3 = (255, 255, 255)
    assert color_distance(c1, c3) > 400.0

def test_contrast_ratio():
    black = (0, 0, 0)
    white = (255, 255, 255)
    ratio = calculate_contrast_ratio(black, white)
    assert ratio >= 20.0 # Maximum WCAG ratio is 21:1

    same = (128, 128, 128)
    assert round(calculate_contrast_ratio(same, same), 1) == 1.0


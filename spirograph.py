import hashlib
from random import Random
from math import sin, cos

from PIL import Image
from numpy import array

def generate_spirograph_points(R, r, p, length):
    a = 0.0
    points = []
    while a < length:
        x = (R - r) * cos(a) + p * cos(((R - r) / r) * a)
        y = (R - r) * sin(a) - p * sin(((R - r) / r) * a)
        points.append((x, y))
        a += 0.01
    return points

def sha256_lower_long(str):
    acc = 0
    for byte in hashlib.sha256(bytes(str, "utf-8")).digest():
        acc = (acc << 8) | (byte & 0xFF)
    return acc

def spirograph(seed: str, width: int, height: int, length: int) -> Image.Image:
    rng = Random(sha256_lower_long(seed))
    line_color = (
        rng.randint(0, 255),
        rng.randint(0, 255),
        rng.randint(0, 255),
    )
    img_array = array(
        [[(0, 0, 0) for _ in range(height)] for _ in range(width)], dtype="uint8"
    )
    R = rng.randint(50, 150)
    r = rng.randint(10, 50)
    p = rng.randint(10, 50)
    points = generate_spirograph_points(R, r, p, length)
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    scale_x = (width - 20) / (max_x - min_x)
    scale_y = (height - 20) / (max_y - min_y)
    for point in points:
        x = int((point[0] - min_x) * scale_x) + 10
        y = int((point[1] - min_y) * scale_y) + 10
        if 2 <= x < width-2 and 2 <= y < height-2:
            img_array[x-2:x+2, y-2:y+2] = line_color
    return Image.fromarray(img_array, "RGB")

spirograph("nickster", 2000, 2000, 1000).show()
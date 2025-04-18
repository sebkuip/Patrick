from math import sin, cos, sqrt, log, ceil
import hashlib
from random import Random
from PIL import Image

class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(
                self.real * other.real - self.imag * other.imag,
                self.real * other.imag + self.imag * other.real,
            )
        if isinstance(other, (int, float)):
            return Complex(self.real * other, self.imag * other)

    def square(self):
        return Complex(
            self.real * self.real - self.imag * self.imag,
            2 * self.real * self.imag,
        )

    def mag2(self):
        return self.real * self.real + self.imag * self.imag

# room for improvement but works 99.9% of times (never crashes just gives up and returns a bad one)
def find_good_julia(angle, messiness):
    x = cos(angle) * 0.4 - 0.3
    y = sin(angle) * 0.4
    coord = Complex(x, y)
    step = coord * 0.005
    for _ in range(1000):
        coord += step
        if mandel_pixel(coord, messiness + 1) <= messiness:
            return coord
    # bad luck, will get an almost blank image
    return Complex(16.0, 0.0)

def sha256_lower_long(str):
    acc = 0
    for byte in hashlib.sha256(bytes(str, "utf-8")).digest():
        acc = (acc << 8) | (byte & 0xFF)
    return acc

def mandel_pixel(coord: Complex, max_iterations: int) -> int:
    z = Complex(0.0, 0.0)
    i = 0
    while i < max_iterations and z.mag2() <= 4.0:
        z = z.square() + coord
        i += 1
    return i

def get_color(i: float, a: float, b: float, c: float) -> tuple:
    red = int(max(sin(i * a) * 255.0, 0.0))
    green = int(max(sin(i * b) * 255.0, 0.0))
    blue = int(max(sin(i * c) * 255.0, 0.0))
    return (red, green, blue)

def julia_pixel(coordinate: Complex, max_iterations: int, c: Complex) -> float:
    z = coordinate
    i = 0
    while i < max_iterations and z.mag2() < 4.0:
        z = z.square() + c
        i += 1
    if i >= max_iterations:
        return float(i)

    for _ in range(3):
        z = z.square() + c
        i += 1

    # actual magic
    return float(i) + 1.0 - log(log(sqrt(z.mag2()))) * (1 / log(2))

def fractal(seed: str, width: int, height: int,  max_iterations: int, messiness: int, zoom: float):
    aspect_ratio = float(width) / float(height)
    rng = Random(sha256_lower_long(seed))

    angle = rng.uniform(-3.14, 3.14)
    seed_coordinate = find_good_julia(angle, messiness)

    a = rng.uniform(0.0, 0.2)
    b = rng.uniform(0.0, 0.2)
    c = rng.uniform(0.0, 0.2)

    img = Image.new("RGB", (width, height), (0, 0, 0))
    for y in range(height):
        for x in range(int(ceil(float(width) / 2.0))):
            co_x = aspect_ratio * zoom * (float(x) / float(width) - 0.5)
            co_y = zoom * (float(y) / float(height) - 0.5)
            coordinate = Complex(co_x, co_y)
            iterations = julia_pixel(coordinate, max_iterations, seed_coordinate)
            color = get_color(iterations, a, b, c)
            img.putpixel((x, y), color)
            img.putpixel((width - x - 1, height - y - 1), color)
    return img

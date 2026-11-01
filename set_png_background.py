#!/usr/bin/env python3
"""Flatten a PNG onto a white background."""

import argparse
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="PNG image to update")
    image_path = parser.parse_args().image

    image = Image.open(image_path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    background.convert("RGB").save(image_path)


if __name__ == "__main__":
    main()

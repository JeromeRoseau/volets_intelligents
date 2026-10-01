"""Icône et logo fournis par l'intégration (dossier brand/, Home Assistant 2026.3 et plus)."""

from pathlib import Path

import pytest
from PIL import Image

BRAND = Path(__file__).parents[1] / "custom_components" / "volets_intelligents" / "brand"


@pytest.mark.parametrize("prefix", ["", "dark_"])
def test_brand_images_have_expected_sizes(prefix):
    assert Image.open(BRAND / f"{prefix}icon.png").size == (256, 256)
    assert Image.open(BRAND / f"{prefix}icon@2x.png").size == (512, 512)
    for name, short_side in ((f"{prefix}logo.png", 256), (f"{prefix}logo@2x.png", 512)):
        width, height = Image.open(BRAND / name).size
        assert height == short_side and width > height

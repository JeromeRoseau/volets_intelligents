"""Tests de la géométrie solaire (sans Home Assistant)."""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from custom_components.volets_intelligents.solar import (
    angular_distance,
    exposure_windows,
    facade_azimuth,
    is_exposed,
    sun_position,
)

LAT, LON, ALT = 45.58, 4.81, 200  # région lyonnaise
PARIS = ZoneInfo("Europe/Paris")


def test_cardinal_facades_of_an_aligned_house():
    assert facade_azimuth("north", 0, 180) == 0
    assert facade_azimuth("east", 0, 180) == 90
    assert facade_azimuth("south", 0, 180) == 180
    assert facade_azimuth("west", 0, 180) == 270


def test_facades_rotate_with_the_house():
    # La façade « Sud » regarde le sud-est : tout tourne de 45°.
    assert facade_azimuth("south", 0, 135) == 135
    assert facade_azimuth("east", 0, 135) == 45
    assert facade_azimuth("north", 0, 135) == 315
    assert facade_azimuth("west", 0, 135) == 225


def test_custom_azimuth_is_absolute():
    assert facade_azimuth("custom", 225, 90) == 225
    assert facade_azimuth("custom", 370, 90) == 10


@pytest.mark.parametrize(
    ("a", "b", "expected"), [(10, 350, 20), (0, 180, 180), (90, 90, 0), (359, 1, 2)]
)
def test_angular_distance_wraps_around_north(a, b, expected):
    assert angular_distance(a, b) == expected


def test_sun_position_noon_in_summer_is_south_and_high():
    # Midi solaire vers 13 h 50 (heure d'été) à la longitude 4,8 °E.
    when = datetime(2026, 6, 21, 11, 50, tzinfo=UTC)
    azimuth, elevation = sun_position(LAT, LON, ALT, when)
    assert 175 < azimuth < 190
    assert 66 < elevation < 69


def test_sun_position_morning_is_east_and_evening_is_west():
    morning = sun_position(LAT, LON, ALT, datetime(2026, 6, 21, 7, 0, tzinfo=UTC))
    evening = sun_position(LAT, LON, ALT, datetime(2026, 6, 21, 17, 0, tzinfo=UTC))
    assert 60 < morning[0] < 120
    assert 240 < evening[0] < 300


def test_is_exposed_requires_height_and_direction():
    assert is_exposed(180, 40, 180, 80, 10)
    assert is_exposed(250, 40, 180, 80, 10)  # 70° d'écart : encore exposé
    assert not is_exposed(270, 40, 180, 80, 10)  # 90° d'écart
    assert not is_exposed(180, 5, 180, 80, 10)  # soleil trop bas


def test_seasons_change_the_exposure_windows():
    south = facade_azimuth("south", 0, 180)
    summer = exposure_windows(LAT, LON, ALT, date(2026, 6, 21), PARIS, south, 80, 10)
    winter = exposure_windows(LAT, LON, ALT, date(2026, 12, 21), PARIS, south, 80, 10)
    assert len(summer) == 1 and len(winter) == 1
    # Le soleil d'été reste utile plus tard dans l'après-midi que celui d'hiver.
    end_summer = summer[0][1].hour * 60 + summer[0][1].minute
    end_winter = winter[0][1].hour * 60 + winter[0][1].minute
    assert end_summer - end_winter > 60


def test_east_facade_is_sunny_in_the_morning_only():
    east = facade_azimuth("east", 0, 180)
    (window,) = exposure_windows(LAT, LON, ALT, date(2026, 9, 30), PARIS, east, 80, 10)
    assert window[0].hour < 9
    assert window[1].hour <= 13


def test_north_facade_gets_sun_only_on_summer_mornings_and_evenings():
    north = facade_azimuth("north", 0, 180)
    summer = exposure_windows(LAT, LON, ALT, date(2026, 6, 21), PARIS, north, 80, 10)
    winter = exposure_windows(LAT, LON, ALT, date(2026, 12, 21), PARIS, north, 80, 10)
    assert len(summer) == 2
    assert winter == []


def test_rotated_house_shifts_the_windows():
    aligned = facade_azimuth("south", 0, 180)
    rotated = facade_azimuth("south", 0, 135)  # regarde le sud-est
    day = date(2026, 9, 30)
    (a,) = exposure_windows(LAT, LON, ALT, day, PARIS, aligned, 80, 10)
    (r,) = exposure_windows(LAT, LON, ALT, day, PARIS, rotated, 80, 10)
    assert r[0] <= a[0] and r[1] < a[1]

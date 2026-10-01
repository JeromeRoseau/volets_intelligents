"""Géométrie solaire : orientation des façades et exposition au soleil.

Ce module n'importe pas Home Assistant (seulement `astral`, déjà fourni avec lui).
Les azimuts sont des azimuts de boussole : 0 = Nord, 90 = Est, 180 = Sud, 270 = Ouest.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, tzinfo

from astral import Observer
from astral.sun import azimuth, elevation

ORIENTATION_NORTH = "north"
ORIENTATION_EAST = "east"
ORIENTATION_SOUTH = "south"
ORIENTATION_WEST = "west"
ORIENTATION_CUSTOM = "custom"
ORIENTATIONS = (
    ORIENTATION_NORTH,
    ORIENTATION_EAST,
    ORIENTATION_SOUTH,
    ORIENTATION_WEST,
    ORIENTATION_CUSTOM,
)

# Azimut d'une façade « idéale » : maison alignée sur les points cardinaux.
_CARDINAL_AZIMUTH = {
    ORIENTATION_NORTH: 0.0,
    ORIENTATION_EAST: 90.0,
    ORIENTATION_SOUTH: 180.0,
    ORIENTATION_WEST: 270.0,
}


def facade_azimuth(orientation: str, custom_azimuth: float, house_orientation: float) -> float:
    """Azimut vers lequel regarde une façade.

    `house_orientation` est l'azimut vers lequel regarde la façade « Sud » de la
    maison (180 si la maison est parfaitement alignée). Les autres façades
    tournent avec elle. L'orientation « custom » est un azimut absolu.
    """
    if orientation == ORIENTATION_CUSTOM:
        return float(custom_azimuth) % 360
    return (_CARDINAL_AZIMUTH[orientation] + float(house_orientation) - 180) % 360


def angular_distance(a: float, b: float) -> float:
    """Écart entre deux azimuts, entre 0 et 180 degrés."""
    return abs((a - b + 180) % 360 - 180)


def sun_position(
    latitude: float, longitude: float, altitude: float, when: datetime
) -> tuple[float, float]:
    """Azimut et hauteur du soleil (degrés) à un instant donné (datetime avec fuseau)."""
    observer = Observer(latitude=latitude, longitude=longitude, elevation=altitude)
    return azimuth(observer, when), elevation(observer, when)


def is_exposed(
    sun_azimuth: float,
    sun_elevation: float,
    facade_az: float,
    half_angle: float,
    elevation_min: float,
) -> bool:
    """La façade reçoit-elle le soleil direct ?

    Oui si le soleil est assez haut et dans le demi-angle autour de la normale
    de la façade (80° par défaut : le soleil ne doit pas être quasi rasant).
    """
    if sun_elevation < elevation_min:
        return False
    return angular_distance(sun_azimuth, facade_az) <= half_angle


def exposure_windows(
    latitude: float,
    longitude: float,
    altitude: float,
    day: date,
    tz: tzinfo,
    facade_az: float,
    half_angle: float,
    elevation_min: float,
    step_minutes: int = 5,
) -> list[tuple[datetime, datetime]]:
    """Plages horaires théoriques d'ensoleillement d'une façade pour un jour donné."""
    observer = Observer(latitude=latitude, longitude=longitude, elevation=altitude)
    step = timedelta(minutes=step_minutes)
    midnight = datetime(day.year, day.month, day.day, tzinfo=tz)
    windows: list[tuple[datetime, datetime]] = []
    start: datetime | None = None
    moment = midnight
    end_of_day = midnight + timedelta(days=1)
    while moment < end_of_day:
        exposed = is_exposed(
            azimuth(observer, moment),
            elevation(observer, moment),
            facade_az,
            half_angle,
            elevation_min,
        )
        if exposed and start is None:
            start = moment
        elif not exposed and start is not None:
            windows.append((start, moment))
            start = None
        moment += step
    if start is not None:
        windows.append((start, end_of_day))
    return windows

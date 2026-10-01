"""Tests du moteur de décision (sans Home Assistant)."""

from datetime import UTC, datetime, timedelta

import pytest

from custom_components.volets_intelligents.const import (
    ACTION_CLOSE,
    ACTION_OPEN,
    MODE_AUTO,
    MODE_MANUAL,
    MODE_OFF,
    ST_COOLDOWN,
    ST_DISABLED,
    ST_GRACE,
    ST_MODE_MANUAL,
    ST_MODE_OFF,
    ST_NO_DATA,
    ST_OUTSIDE,
    ST_PAUSED,
    ST_SCENARIO_OFF,
    ST_SHADED,
    ST_UNAVAILABLE,
    ST_WATCHING,
    ST_WIND,
    ST_WINDOW_OPEN,
)
from custom_components.volets_intelligents.engine import (
    CoverInputs,
    CoverRuntime,
    Env,
    decide,
)
from custom_components.volets_intelligents.schema import default_config, normalize_config

NOW = datetime(2026, 7, 15, 14, 0, tzinfo=UTC)
SCENARIOS = normalize_config(default_config())["scenarios"]


def cover(**over):
    base = {
        "entity_id": "cover.salon",
        "name": "Salon",
        "facade": "sud",
        "enabled": True,
        "close_method": "position",
        "close_position": 10,
        "button_entity": None,
        "open_position": 100,
        "room_temp_entity": None,
        "window_entities": [],
        "block_close_if_open": True,
        "wind_sensitive": False,
    }
    base.update(over)
    return base


def inputs(**over):
    base = {
        "available": True,
        "state": "open",
        "position": 100,
        "room_temp": 23.0,
        "window_open": False,
        "exposed": True,
        "facade_name": "Sud",
    }
    base.update(over)
    return CoverInputs(**base)


def env(scenario="summer", **over):
    base = {
        "now": NOW,
        "mode": MODE_AUTO,
        "scenario": SCENARIOS[scenario],
        "in_window": True,
        "grace_active": False,
        "outdoor": 28.0,
        "wind_exceeded": False,
        "tolerance": 3,
        "min_move": timedelta(minutes=10),
    }
    base.update(over)
    return Env(**base)


# --- garde-fous ----------------------------------------------------------------


def test_disabled_cover():
    d = decide(cover(enabled=False), inputs(), CoverRuntime(), env())
    assert (d.status, d.action) == (ST_DISABLED, None)


@pytest.mark.parametrize(
    ("mode", "status"), [(MODE_MANUAL, ST_MODE_MANUAL), (MODE_OFF, ST_MODE_OFF)]
)
def test_global_mode_blocks(mode, status):
    d = decide(cover(), inputs(), CoverRuntime(), env(mode=mode))
    assert (d.status, d.action) == (status, None)


def test_scenario_off_blocks():
    d = decide(cover(), inputs(), CoverRuntime(), env(scenario="off"))
    assert d.status == ST_SCENARIO_OFF and d.action is None


def test_unavailable_cover_does_nothing():
    d = decide(cover(), inputs(available=False), CoverRuntime(), env())
    assert (d.status, d.action) == (ST_UNAVAILABLE, None)


def test_startup_grace_blocks_actions():
    d = decide(cover(), inputs(), CoverRuntime(), env(grace_active=True))
    assert (d.status, d.action) == (ST_GRACE, None)


def test_pause_blocks_then_expires():
    rt = CoverRuntime(paused_until=NOW + timedelta(minutes=30))
    assert decide(cover(), inputs(), rt, env()).status == ST_PAUSED
    rt = CoverRuntime(paused_until=NOW - timedelta(minutes=1))
    assert decide(cover(), inputs(), rt, env()).action == ACTION_CLOSE


def test_no_data_when_outdoor_missing_never_acts():
    # Régression de l'ancienne automatisation : capteur indisponible => 0 °C => ouverture.
    shaded = inputs(position=10, state="open")
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), shaded, rt, env(outdoor=None))
    assert (d.status, d.action) == (ST_NO_DATA, None)


# --- protection thermique -------------------------------------------------------


def test_close_when_exposed_and_hot_outside():
    d = decide(cover(), inputs(), CoverRuntime(), env(outdoor=26))
    assert (d.status, d.action) == (ST_SHADED, ACTION_CLOSE)
    assert "Sud" in d.reason and "26" in d.reason


def test_close_when_room_is_hot():
    d = decide(cover(), inputs(room_temp=25), CoverRuntime(), env(outdoor=20))
    assert d.action == ACTION_CLOSE


def test_no_close_without_sun():
    d = decide(cover(), inputs(exposed=False), CoverRuntime(), env(outdoor=35))
    assert (d.status, d.action) == (ST_WATCHING, None)


def test_no_close_when_cool_enough():
    d = decide(cover(), inputs(room_temp=22), CoverRuntime(), env(outdoor=24))
    assert (d.status, d.action) == (ST_WATCHING, None)


def test_already_at_target_position_is_not_ours():
    d = decide(cover(), inputs(position=10), CoverRuntime(), env())
    assert (d.status, d.action) == (ST_WATCHING, None)


def test_window_open_blocks_close():
    d = decide(cover(), inputs(window_open=True), CoverRuntime(), env())
    assert (d.status, d.action) == (ST_WINDOW_OPEN, None)


def test_window_open_allowed_when_not_blocking():
    c = cover(block_close_if_open=False)
    d = decide(c, inputs(window_open=True), CoverRuntime(), env())
    assert d.action == ACTION_CLOSE


def test_cooldown_blocks_close():
    rt = CoverRuntime(last_command_at=NOW - timedelta(minutes=3))
    d = decide(cover(), inputs(), rt, env())
    assert (d.status, d.action) == (ST_COOLDOWN, None)


def test_stay_shaded_while_sun_and_hot():
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=10, room_temp=21), rt, env(outdoor=27))
    assert (d.status, d.action) == (ST_SHADED, None)


def test_release_all_mode_needs_both_cool():
    rt = CoverRuntime(shaded_by_us=True)
    # La pièce a refroidi grâce au volet mais il fait toujours chaud dehors : on reste fermé.
    d = decide(cover(), inputs(position=10, room_temp=21), rt, env(outdoor=26))
    assert d.action is None
    d = decide(cover(), inputs(position=10, room_temp=21), rt, env(outdoor=20))
    assert d.action == ACTION_OPEN


def test_release_any_mode_opens_when_room_cool():
    scenario = {**SCENARIOS["summer"], "release_mode": "any"}
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(
        cover(),
        inputs(position=10, room_temp=21),
        rt,
        env(outdoor=26, scenario="summer").__class__(
            **{**env(outdoor=26).__dict__, "scenario": scenario}
        ),
    )
    assert d.action == ACTION_OPEN


def test_release_when_sun_leaves_facade():
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=10, exposed=False), rt, env(outdoor=30))
    assert d.action == ACTION_OPEN


def test_release_respects_cooldown():
    rt = CoverRuntime(shaded_by_us=True, last_command_at=NOW - timedelta(minutes=2))
    d = decide(cover(), inputs(position=10, exposed=False), rt, env())
    assert (d.status, d.action) == (ST_COOLDOWN, None)


def test_never_reopen_a_cover_the_user_closed():
    # Volet fermé à la main (pas par nous) : on ne le rouvre jamais.
    d = decide(cover(), inputs(position=0, state="closed", exposed=False), CoverRuntime(), env())
    assert d.action is None


def test_stale_shaded_flag_ignored_when_cover_is_open():
    # Le drapeau dit « protégé » mais le volet est ouvert : incohérence => pas d'ouverture.
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=100, exposed=False), rt, env())
    assert d.action is None


def test_lift_at_end_of_window_only_for_our_covers():
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=10), rt, env(in_window=False))
    assert (d.status, d.action) == (ST_OUTSIDE, ACTION_OPEN)
    d = decide(cover(), inputs(position=10), CoverRuntime(), env(in_window=False))
    assert (d.status, d.action) == (ST_OUTSIDE, None)


def test_state_only_cover_without_position():
    d = decide(cover(), inputs(position=None, state="open"), CoverRuntime(), env())
    assert d.action == ACTION_CLOSE
    d = decide(cover(), inputs(position=None, state="closed"), CoverRuntime(), env())
    assert d.action is None


# --- vent -----------------------------------------------------------------------


def test_wind_retracts_sensitive_cover_even_when_paused():
    rt = CoverRuntime(paused_until=NOW + timedelta(hours=1))
    c = cover(wind_sensitive=True)
    d = decide(c, inputs(position=10), rt, env(wind_exceeded=True))
    assert (d.status, d.action) == (ST_WIND, ACTION_OPEN)


def test_wind_ignored_for_insensitive_cover():
    d = decide(cover(), inputs(), CoverRuntime(), env(wind_exceeded=True))
    assert d.status != ST_WIND


# --- autres scénarios -----------------------------------------------------------


def test_vacation_shades_whenever_exposed_regardless_of_temperature():
    d = decide(cover(), inputs(), CoverRuntime(), env("vacation", outdoor=5))
    assert d.action == ACTION_CLOSE
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=10, exposed=False), rt, env("vacation"))
    assert d.action == ACTION_OPEN


def test_winter_opens_for_solar_gain_only_when_cold():
    d = decide(
        cover(),
        inputs(position=0, state="closed", room_temp=18),
        CoverRuntime(),
        env("winter", outdoor=8),
    )
    assert d.action == ACTION_OPEN
    d = decide(
        cover(),
        inputs(position=0, state="closed", room_temp=22),
        CoverRuntime(),
        env("winter", outdoor=8),
    )
    assert d.action is None
    d = decide(
        cover(),
        inputs(position=0, state="closed", room_temp=18, exposed=False),
        CoverRuntime(),
        env("winter", outdoor=8),
    )
    assert d.action is None


# --- régressions de la relecture indépendante -----------------------------------


def test_unknown_exposure_means_no_data_and_no_action():
    rt = CoverRuntime(shaded_by_us=True)
    d = decide(cover(), inputs(position=10, exposed=None), rt, env())
    assert (d.status, d.action) == (ST_NO_DATA, None)


def test_wind_beats_mode_scenario_and_startup_delay():
    c = cover(wind_sensitive=True, wind_action="open")
    for kwargs in (
        {"mode": MODE_MANUAL},
        {"mode": MODE_OFF},
        {"grace_active": True},
        {"scenario": "off"},
    ):
        d = decide(c, inputs(position=10), CoverRuntime(), env(wind_exceeded=True, **kwargs))
        assert (d.status, d.action, d.plain) == (ST_WIND, ACTION_OPEN, True), kwargs


def test_wind_respects_an_explicitly_disabled_cover():
    c = cover(wind_sensitive=True, enabled=False)
    d = decide(c, inputs(position=10), CoverRuntime(), env(wind_exceeded=True))
    assert (d.status, d.action) == (ST_DISABLED, None)


def test_awning_retracts_with_close_and_stays_put_once_closed():
    c = cover(wind_sensitive=True, wind_action="close")
    d = decide(c, inputs(position=60), CoverRuntime(), env(wind_exceeded=True))
    assert (d.action, d.plain) == (ACTION_CLOSE, True)
    d = decide(c, inputs(position=0, state="closed"), CoverRuntime(), env(wind_exceeded=True))
    assert d.action is None


def test_cover_stopping_above_target_is_still_recognised_as_ours():
    rt = CoverRuntime(shaded_by_us=True)
    shaded_at_35 = inputs(position=35, exposed=True)
    assert decide(cover(), shaded_at_35, rt, env(outdoor=28)).action is None
    released = inputs(position=35, exposed=False)
    assert decide(cover(), released, rt, env()).action == ACTION_OPEN


def test_winter_solar_gain_respects_cooldown():
    rt = CoverRuntime(last_command_at=NOW - timedelta(minutes=2))
    d = decide(
        cover(),
        inputs(position=0, state="closed", room_temp=18),
        rt,
        env("winter", outdoor=8),
    )
    assert (d.status, d.action) == (ST_COOLDOWN, None)

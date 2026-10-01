"""Simulation d'une journée chaude complète avec des volets qui bougent vraiment."""

from unittest.mock import patch

from homeassistant.components.cover import CoverEntityFeature
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.volets_intelligents.const import DOMAIN
from custom_components.volets_intelligents.schema import default_config

FEATURES = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION
COVERS = {
    "cover.est": "est",
    "cover.sud": "sud",
    "cover.ouest": "ouest",
    "cover.nord": "nord",
}


def _config():
    cfg = default_config()
    cfg["settings"].update(
        {
            "outdoor_temp_entity": "sensor.dehors",
            "startup_grace_seconds": 0,
            "min_move_interval_minutes": 10,
            "window": {"start": "08:00", "end_mode": "fixed", "end_time": "19:00"},
        }
    )
    cfg["covers"] = [
        {"entity_id": eid, "name": facade.title(), "facade": facade, "close_position": 10}
        for eid, facade in COVERS.items()
    ]
    return cfg


async def test_hot_july_day_follows_the_sun_around_the_house(hass, hass_storage, freezer):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.latitude, hass.config.longitude, hass.config.elevation = 45.58, 4.81, 200
    freezer.move_to("2026-07-15 07:00:00+02:00")
    hass.config.components.update({"frontend", "panel_custom", "http", "websocket_api"})
    hass_storage["volets_intelligents.config"] = {
        "version": 1,
        "minor_version": 1,
        "key": "volets_intelligents.config",
        "data": _config(),
    }

    positions = dict.fromkeys(COVERS, 100)

    def publish(entity_id):
        hass.states.async_set(
            entity_id,
            "open" if positions[entity_id] > 0 else "closed",
            {"current_position": positions[entity_id], "supported_features": FEATURES},
        )

    async def set_position(call):
        positions[call.data["entity_id"]] = call.data["position"]
        publish(call.data["entity_id"])

    async def open_cover(call):
        positions[call.data["entity_id"]] = 100
        publish(call.data["entity_id"])

    hass.services.async_register("cover", "set_cover_position", set_position)
    hass.services.async_register("cover", "open_cover", open_cover)
    for entity_id in COVERS:
        publish(entity_id)
    hass.states.async_set("sensor.dehors", "30")

    entry = MockConfigEntry(domain=DOMAIN, title="Volets Intelligents")
    entry.add_to_hass(hass)
    with patch("custom_components.volets_intelligents._async_register_frontend"):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        manager = entry.runtime_data

        timeline = {}
        for hour in range(8, 21):
            for minute in (0, 30):
                freezer.move_to(f"2026-07-15 {hour:02d}:{minute:02d}:00+02:00")
                await manager.async_evaluate()
                await hass.async_block_till_done()
                timeline[f"{hour:02d}:{minute:02d}"] = dict(positions)

        # Le matin, seule la façade est est protégée ; le sud l'est en milieu de journée ;
        # l'ouest en fin d'après-midi ; le nord n'est pas protégé en plein jour.
        assert timeline["09:00"]["cover.est"] == 10
        assert timeline["09:00"]["cover.ouest"] == 100
        assert timeline["13:00"]["cover.sud"] == 10
        assert timeline["16:00"]["cover.ouest"] == 10
        # (le nord reçoit le soleil rasant tôt le matin et tard le soir en été, pas en journée)
        assert all(timeline[t]["cover.nord"] == 100 for t in ("10:00", "12:00", "14:00", "16:00"))
        # Quand le soleil quitte une façade, son volet est remonté.
        assert timeline["14:00"]["cover.est"] == 100
        # À la fin de la plage active (19:00) tout est remonté.
        assert timeline["19:30"] == dict.fromkeys(COVERS, 100)
        assert timeline["20:30"] == dict.fromkeys(COVERS, 100)

    if entry.state is ConfigEntryState.LOADED:
        await hass.config_entries.async_unload(entry.entry_id)
    # Garde-fou anti-usure : pas plus de 3 mouvements par volet dans la journée.
    moves = {
        eid: sum(
            1
            for prev, cur in zip(list(timeline.values()), list(timeline.values())[1:], strict=False)
            if prev[eid] != cur[eid]
        )
        for eid in COVERS
    }
    assert all(count <= 3 for count in moves.values()), moves

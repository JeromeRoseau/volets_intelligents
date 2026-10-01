from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.volets_intelligents.const import DOMAIN


async def _result(ws, msg_id):
    """Lit les messages jusqu'au résultat voulu (des événements de statut peuvent s'intercaler)."""
    while True:
        message = await ws.receive_json()
        if message.get("type") == "result" and message["id"] == msg_id:
            return message


async def test_real_frontend_registration(hass, hass_client, hass_ws_client):
    assert await async_setup_component(hass, "http", {})
    assert await async_setup_component(hass, "frontend", {})
    entry = MockConfigEntry(domain=DOMAIN, title="Volets Intelligents")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    client = await hass_client()
    for name in ("volets-panel.js", "volets-card.js"):
        resp = await client.get(f"/volets_intelligents_static/{name}")
        assert resp.status == 200, name
        assert "customElements.define" in await resp.text()
    panels = hass.data["frontend_panels"]
    assert "volets-intelligents" in panels
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "volets_intelligents/get_config"})
    res = await ws.receive_json()
    assert res["success"], res
    cfg = res["result"]["config"]
    cfg["facades"] = [{"id": "sud", "name": "Sud", "exposure": {"mode": "sun"}}]
    cfg["covers"] = [{"entity_id": "cover.x", "facade": "sud"}]
    await ws.send_json({"id": 2, "type": "volets_intelligents/set_config", "config": cfg})
    res = await ws.receive_json()
    assert res["success"], res
    await ws.send_json(
        {
            "id": 3,
            "type": "volets_intelligents/set_config",
            "config": {**cfg, "covers": [{"entity_id": "cover.x", "facade": "nope"}]},
        }
    )
    res = await ws.receive_json()
    assert (
        not res["success"]
        and res["error"]["code"] == "invalid_config"
        and "nope" in res["error"]["message"]
    )
    await ws.send_json({"id": 4, "type": "volets_intelligents/subscribe_status"})
    res = await ws.receive_json()
    assert res["success"]
    ev = await ws.receive_json()
    assert ev["type"] == "event" and ev["event"]["covers"][0]["entity_id"] == "cover.x"
    await ws.send_json(
        {"id": 5, "type": "volets_intelligents/command", "command": "set_mode", "value": "manual"}
    )
    res = await _result(ws, 5)
    assert res["success"]
    await ws.send_json(
        {"id": 6, "type": "volets_intelligents/command", "command": "set_scenario", "value": "nope"}
    )
    res = await _result(ws, 6)
    assert not res["success"] and res["error"]["code"] == "command_failed"
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert "volets-intelligents" not in hass.data["frontend_panels"]

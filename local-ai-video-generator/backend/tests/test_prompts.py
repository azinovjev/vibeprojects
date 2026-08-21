from __future__ import annotations


def test_seeded_presets_available(app_client):
    response = app_client.get("/api/prompts")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 2


def test_create_update_delete_prompt(app_client):
    created = app_client.post(
        "/api/prompts", json={"name": "My preset", "prompt_text": "Move the clouds slowly."}
    )
    assert created.status_code == 201
    preset = created.json()
    assert preset["name"] == "My preset"

    updated = app_client.put(
        f"/api/prompts/{preset['id']}",
        json={"name": "My preset v2", "prompt_text": "Move the clouds quickly."},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "My preset v2"

    deleted = app_client.delete(f"/api/prompts/{preset['id']}")
    assert deleted.status_code == 204

    missing_update = app_client.put(
        f"/api/prompts/{preset['id']}", json={"name": "x", "prompt_text": "y"}
    )
    assert missing_update.status_code == 404


def test_create_prompt_rejects_empty_text(app_client):
    response = app_client.post("/api/prompts", json={"name": "Bad", "prompt_text": ""})
    assert response.status_code == 422


def test_delete_missing_prompt_returns_404(app_client):
    response = app_client.delete("/api/prompts/does-not-exist")
    assert response.status_code == 404

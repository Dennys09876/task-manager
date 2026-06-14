"""
Pruebas negativas – verifican que el sistema rechaza entradas inválidas correctamente.
"""


def test_create_task_missing_title(client):
    """Crear tarea sin título devuelve 400."""
    res = client.post("/api/tasks", json={"description": "Sin título"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_task_empty_title(client):
    """Crear tarea con título vacío devuelve 400."""
    res = client.post("/api/tasks", json={"title": "   "})
    assert res.status_code == 400


def test_create_task_invalid_status(client):
    """Crear tarea con estado inválido devuelve 400."""
    res = client.post("/api/tasks", json={"title": "Test", "status": "invalido"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_task_no_body(client):
    """Crear tarea sin body JSON devuelve 400."""
    res = client.post("/api/tasks", content_type="application/json", data="")
    assert res.status_code == 400


def test_get_nonexistent_task(client):
    """Obtener una tarea que no existe devuelve 404."""
    res = client.get("/api/tasks/9999")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_update_nonexistent_task(client):
    """Actualizar una tarea que no existe devuelve 404."""
    res = client.put("/api/tasks/9999", json={"title": "Ghost"})
    assert res.status_code == 404


def test_delete_nonexistent_task(client):
    """Eliminar una tarea que no existe devuelve 404."""
    res = client.delete("/api/tasks/9999")
    assert res.status_code == 404


def test_update_task_empty_title(client):
    """Actualizar tarea con título vacío devuelve 400."""
    created = client.post("/api/tasks", json={"title": "Valida"}).get_json()
    res = client.put(f"/api/tasks/{created['id']}", json={"title": ""})
    assert res.status_code == 400


def test_update_task_invalid_status(client):
    """Actualizar tarea con estado inválido devuelve 400."""
    created = client.post("/api/tasks", json={"title": "Ok"}).get_json()
    res = client.put(f"/api/tasks/{created['id']}", json={"status": "unknown"})
    assert res.status_code == 400


def test_filter_invalid_status(client):
    """Filtrar por estado inválido devuelve 400."""
    res = client.get("/api/tasks?status=xyz")
    assert res.status_code == 400

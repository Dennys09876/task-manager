"""
Pruebas de borde – verifican los límites del sistema.
"""


def test_title_exactly_200_chars(client):
    """Título con exactamente 200 caracteres es aceptado."""
    title = "A" * 200
    res = client.post("/api/tasks", json={"title": title})
    assert res.status_code == 201
    assert res.get_json()["title"] == title


def test_title_201_chars_rejected(client):
    """Título con 201 caracteres es rechazado con 400."""
    title = "A" * 201
    res = client.post("/api/tasks", json={"title": title})
    assert res.status_code == 400


def test_title_one_char(client):
    """Título con un solo carácter es aceptado."""
    res = client.post("/api/tasks", json={"title": "X"})
    assert res.status_code == 201


def test_all_valid_statuses(client):
    """Los tres estados válidos son aceptados al crear."""
    for status in ("pending", "in_progress", "completed"):
        res = client.post("/api/tasks", json={"title": f"Tarea {status}", "status": status})
        assert res.status_code == 201, f"Fallo con status={status}"
        assert res.get_json()["status"] == status


def test_all_status_transitions(client):
    """Se puede transitar entre cualquier combinación de estados."""
    created = client.post("/api/tasks", json={"title": "Ciclo"}).get_json()
    tid = created["id"]
    for status in ("in_progress", "completed", "pending", "in_progress"):
        res = client.put(f"/api/tasks/{tid}", json={"status": status})
        assert res.status_code == 200
        assert res.get_json()["status"] == status


def test_description_can_be_null(client):
    """Una tarea sin descripción es válida y description es null."""
    res = client.post("/api/tasks", json={"title": "Sin desc"})
    assert res.status_code == 201
    assert res.get_json()["description"] is None


def test_description_can_be_empty_string(client):
    """Descripción con string vacío se guarda como null."""
    res = client.post("/api/tasks", json={"title": "Desc vacía", "description": ""})
    assert res.status_code == 201
    assert res.get_json()["description"] is None


def test_create_many_tasks(client):
    """El sistema maneja la creación de múltiples tareas sin errores."""
    for i in range(50):
        res = client.post("/api/tasks", json={"title": f"Tarea {i}"})
        assert res.status_code == 201
    res = client.get("/api/tasks")
    assert len(res.get_json()) == 50


def test_title_with_special_characters(client):
    """Títulos con caracteres especiales y acentos son aceptados."""
    title = "Tarea: diseño & arquitectura <sistema> ñoño"
    res = client.post("/api/tasks", json={"title": title})
    assert res.status_code == 201
    assert res.get_json()["title"] == title


def test_update_with_no_changes(client):
    """PUT sin cambios relevantes devuelve 200 con datos actuales."""
    created = client.post("/api/tasks", json={"title": "Sin cambios"}).get_json()
    res = client.put(f"/api/tasks/{created['id']}", json={"description": "algo"})
    assert res.status_code == 200

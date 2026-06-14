"""
Pruebas funcionales – verifican el comportamiento esperado del sistema.
"""
import json


def test_health_check(client):
    """El endpoint de salud responde 200."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"


def test_create_task(client):
    """Crear una tarea con datos válidos devuelve 201 y los datos correctos."""
    payload = {"title": "Diseñar base de datos", "description": "Modelo ER", "status": "pending"}
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] is not None
    assert data["title"] == "Diseñar base de datos"
    assert data["status"] == "pending"


def test_list_tasks_empty(client):
    """Listar tareas cuando no hay ninguna devuelve lista vacía."""
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_tasks(client):
    """Listar tareas devuelve todas las creadas."""
    client.post("/api/tasks", json={"title": "Tarea A"})
    client.post("/api/tasks", json={"title": "Tarea B"})
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_task_by_id(client):
    """Obtener una tarea por ID devuelve los datos correctos."""
    created = client.post("/api/tasks", json={"title": "Mi tarea"}).get_json()
    res = client.get(f"/api/tasks/{created['id']}")
    assert res.status_code == 200
    assert res.get_json()["title"] == "Mi tarea"


def test_update_task_title(client):
    """Actualizar el título de una tarea devuelve el nuevo valor."""
    created = client.post("/api/tasks", json={"title": "Original"}).get_json()
    res = client.put(f"/api/tasks/{created['id']}", json={"title": "Actualizado"})
    assert res.status_code == 200
    assert res.get_json()["title"] == "Actualizado"


def test_update_task_status(client):
    """Cambiar el estado de pending a completed funciona correctamente."""
    created = client.post("/api/tasks", json={"title": "Hacer CI"}).get_json()
    res = client.put(f"/api/tasks/{created['id']}", json={"status": "completed"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "completed"


def test_update_task_all_fields(client):
    """Actualizar todos los campos a la vez funciona correctamente."""
    created = client.post("/api/tasks", json={"title": "Vieja"}).get_json()
    res = client.put(
        f"/api/tasks/{created['id']}",
        json={"title": "Nueva", "description": "Desc", "status": "in_progress"},
    )
    data = res.get_json()
    assert res.status_code == 200
    assert data["title"] == "Nueva"
    assert data["description"] == "Desc"
    assert data["status"] == "in_progress"


def test_delete_task(client):
    """Eliminar una tarea existente devuelve 200 y la tarea no existe después."""
    created = client.post("/api/tasks", json={"title": "Borrar esta"}).get_json()
    res = client.delete(f"/api/tasks/{created['id']}")
    assert res.status_code == 200
    res2 = client.get(f"/api/tasks/{created['id']}")
    assert res2.status_code == 404


def test_filter_by_status(client):
    """Filtrar tareas por estado devuelve solo las del estado indicado."""
    client.post("/api/tasks", json={"title": "T1", "status": "pending"})
    client.post("/api/tasks", json={"title": "T2", "status": "completed"})
    client.post("/api/tasks", json={"title": "T3", "status": "completed"})

    res = client.get("/api/tasks?status=completed")
    tasks = res.get_json()
    assert res.status_code == 200
    assert len(tasks) == 2
    assert all(t["status"] == "completed" for t in tasks)


def test_task_default_status_is_pending(client):
    """Si no se envía estado, la tarea se crea con estado 'pending'."""
    res = client.post("/api/tasks", json={"title": "Sin estado"})
    assert res.get_json()["status"] == "pending"

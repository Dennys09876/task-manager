from flask import Blueprint, jsonify, request
from app import db
from app.models import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api")

VALID_STATUSES = {"pending", "in_progress", "completed"}


@tasks_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "task-manager"}), 200


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    status_filter = request.args.get("status")
    query = Task.query

    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": f"Estado inválido: {status_filter}"}), 400
        query = query.filter_by(status=status_filter)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400
    if len(title) > 200:
        return jsonify({"error": "El título no puede superar 200 caracteres"}), 400

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"Estado inválido: {status}"}), 400

    task = Task(
        title=title,
        description=data.get("description", "").strip() or None,
        status=status,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "El título no puede estar vacío"}), 400
        if len(title) > 200:
            return jsonify({"error": "El título no puede superar 200 caracteres"}), 400
        task.title = title

    if "description" in data:
        task.description = data["description"].strip() or None

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Estado inválido: {data['status']}"}), 400
        task.status = data["status"]

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Tarea {task_id} eliminada correctamente"}), 200

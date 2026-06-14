#!/bin/bash
# Ejecuta el suite de pruebas con reporte de cobertura

set -e

echo "=== [TEST] Ejecutando pruebas Task Manager ==="
echo "Fecha: $(date)"
echo ""

export FLASK_ENV=testing

source venv/bin/activate 2>/dev/null || true

echo "[1/3] Pruebas funcionales..."
pytest tests/test_functional.py -v 2>&1

echo ""
echo "[2/3] Pruebas negativas..."
pytest tests/test_negative.py -v 2>&1

echo ""
echo "[3/3] Pruebas de borde..."
pytest tests/test_boundary.py -v 2>&1

echo ""
echo "=== Reporte de cobertura ==="
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:reports/coverage 2>&1

echo ""
echo "=== Pruebas completadas ==="
echo "Reporte HTML: reports/coverage/index.html"

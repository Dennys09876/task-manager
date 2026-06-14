#!/bin/bash
# Instala dependencias del proyecto en un virtualenv

set -e

echo "=== [INSTALL] Task Manager Setup ==="

if ! command -v python3 &>/dev/null; then
  echo "ERROR: Python 3 no encontrado"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "[1/3] Creando entorno virtual..."
  python3 -m venv venv
fi

echo "[2/3] Activando entorno e instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "[3/3] Verificando instalación..."
python -c "import flask; print(f'  Flask {flask.__version__} OK')"
python -c "import flask_sqlalchemy; print(f'  Flask-SQLAlchemy OK')"
python -c "import pytest; print(f'  pytest {pytest.__version__} OK')"

echo ""
echo "=== Instalación completada ==="
echo "Para iniciar el servidor: ./scripts/run.sh dev"

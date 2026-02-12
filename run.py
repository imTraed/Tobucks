"""Punto de entrada de la aplicación Flask"""

import os
from app import create_app
from config import get_config

# Obtener configuración según entorno
config = get_config()

# Crear instancia de la aplicación
app = create_app(config)

# Iniciar servidor Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=5000, debug=True)
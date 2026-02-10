# 🚀 Guía de Despliegue en Heroku (Servicio Gratuito)

## Opción A: Heroku (Recomendado - Gratuito con limitaciones)

### Requisitos:
- Cuenta en [heroku.com](https://heroku.com)
- Git instalado
- Heroku CLI instalado

### Pasos:

#### 1. Preparar localmente
```bash
# Verificar que todo está en git
git init
git add .
git commit -m "Initial commit"
```

#### 2. Crear la app en Heroku
```bash
# Instalar Heroku CLI si no lo tienes
npm install -g heroku

# Loguarse
heroku login

# Crear app
heroku create tu-app-nombre
```

#### 3. Configurar PostgreSQL
```bash
# Agregar base de datos PostgreSQL (plan Hobby, gratuito)
heroku addons:create heroku-postgresql:hobby-dev --app tu-app-nombre

# Esto creará automáticamente la variable DATABASE_URI
```

#### 4. Configurar variables de entorno
```bash
heroku config:set FLASK_ENV=production --app tu-app-nombre
heroku config:set SECRET_KEY="your-super-secret-key-here" --app tu-app-nombre
heroku config:set OMDB_API_KEY="c4a84505" --app tu-app-nombre
heroku config:set GOOGLE_API_KEY="AIzaSyB8N--E-B7yFzPLAgu0AQ3zL3Mv2Ae7Wbs" --app tu-app-nombre
```

#### 5. Hacer push a Heroku
```bash
git push heroku main
# O si tu rama principal es "master":
# git push heroku master
```

#### 6. Crear tablas en la BD
```bash
heroku run flask db upgrade --app tu-app-nombre
# O si es primera vez:
heroku run flask shell --app tu-app-nombre
# Dentro del shell:
# >>> from app import db
# >>> db.create_all()
# >>> exit()
```

#### 7. Migrar datos (opcional)
```bash
# Descargar el respaldo SQL
python export_sql_dump.py

# Importar en PostgreSQL de Heroku
heroku pg:psql --app tu-app-nombre < tobucks_export.sql
```

#### 8. Ver la app
```bash
heroku open --app tu-app-nombre
# O visita: https://tu-app-nombre.herokuapp.com
```

---

## Opción B: PythonAnywhere (Alternativa más simple)

### Pasos:
1. Ir a [pythonawhere.com](https://pythonanywhere.com)
2. Crear cuenta gratuita
3. Subir archivos del proyecto
4. Crear Web app con Flask
5. Configurar variables de entorno en la consola
6. Iniciar la app

**Ventaja**: No necesita Git ni Heroku CLI

---

## Notas Importantes:

### Heroku - Plan Gratuito en 2024:
- ⚠️ El plan Eco es de PAGO (el plan gratuito fue discontinuado)
- **Alternativa gratuita**: Usar Railway, Render o PythonAnywhere
- Heroku Hobby Dev cuesta: $7/mes

### Render (Alternativa GRATUITA a Heroku):
1. Ir a [render.com](https://render.com)
2. Conectar repositorio GitHub
3. Crear Web Service
4. Seleccionar Python 3.9+
5. Build: `pip install -r requirements.txt`
6. Start: `gunicorn run:app`
7. Agregar variables de entorno
8. Crear PostgreSQL database (gratis)

#### Render: Pasos rápidos
```bash
# Solo pushear a GitHub
git push origin main

# En Render.com:
# - Conectar repo
# - Crear Web Service
# - Seleccionar "Public"
# - Build command: pip install -r requirements.txt
# - Start command: gunicorn run:app
# - Variables ENV en Settings
```

---

## Checklist Pre-Despliegue:

- [ ] ✅ Todos los archivos en control de versión (git)
- [ ] ✅ `.env` está en `.gitignore` (no subir secretos)
- [ ] ✅ `requirements.txt` actualizado
- [ ] ✅ `Procfile` presente
- [ ] ✅ `config.py` soporta entorno de producción
- [ ] ✅ BD migrada a PostgreSQL
- [ ] ✅ `SECRET_KEY` configurado en producción
- [ ] ✅ Debug = False en producción

---

## Troubleshooting:

### Heroku - Revisar logs:
```bash
heroku logs --tail --app tu-app-nombre
```

### Error de BD:
```bash
# Resetear BD
heroku pg:reset DATABASE_URL --app tu-app-nombre

# Recrear si es necesario
heroku addons:create heroku-postgresql:hobby-dev --app tu-app-nombre
```

### Variables de entorno:
```bash
# Ver todas
heroku config --app tu-app-nombre

# Establecer una
heroku config:set VAR_NAME=value --app tu-app-nombre

# Eliminar una
heroku config:unset VAR_NAME --app tu-app-nombre
```

---

## Costo Estimado:

| Opción | Costo |
|--------|-------|
| PythonAnywhere | Gratis* / $5 USD/mes |
| Heroku | $7 USD/mes (plan mínimo) |
| Render | Gratis / $7+ USD/mes |
| Railway | Gratis*/privado | $5 créditos/mes |

*Con limitaciones

---

**¿Necesitas ayuda con algún paso?** Ejecuta los scripts en este orden:
1. `python export_sql_dump.py` - Exportar datos
2. Desplegar en servicio de hosting
3. Importar datos en la BD de producción

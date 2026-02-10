# 📋 Guía Completa: Llevar Tobucks a Producción

## ✅ Lo que ya hemos hecho:

1. **Instalado todas las dependencias** (Flask, SQLAlchemy, psycopg2, gunicorn, etc.)
2. **Creado venv** y configurado Python
3. **Actualizado config.py** para soportar múltiples entornos (desarrollo/producción)
4. **Actualizado run.py** para usar variables de entorno
5. **Creado herramientas de migración**:
   - `export_sql_dump.py` → Exporta a SQL genérico
   - `export_json_dump.py` → Exporta a JSON
   - `migrate_to_postgres.py` → Migra directo a PostgreSQL
6. **Preparado archivos de despliegue**:
   - `Procfile` para Heroku
   - `.env.example` con variables necesarias
   - `.gitignore` para proteger secretos

---

## 🚀 Próximos Pasos:

### PASO 1️⃣: Exportar tus datos actuales
```powershell
# Activar venv si no está
.\venv\Scripts\Activate.ps1

# Exportar a SQL (compatible con PostgreSQL, MySQL, SQLite)
python export_sql_dump.py

# O exportar a JSON (más flexible)
python export_json_dump.py
```

**Resultado**: Archivos `tobucks_export.sql` o `tobucks_data_export.json`

---

### PASO 2️⃣: Elegir plataforma de hosting

#### Opción A: RENDER.COM (Recomendado - Gratuito)
**Pros:**
- ✅ Totalmente gratuito para PostgreSQL
- ✅ Base de datos gratuita incluida
- ✅ Fácil de vincular con GitHub
- ✅ Auto-despliegue en cada push

**Pasos:**
1. Ir a [render.com](https://render.com) y crear cuenta
2. Conectar tu repositorio GitHub
3. Crear nuevo "Web Service"
4. Configurar:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `gunicorn run:app`
5. En Variables de Entorno, agregar:
   ```
   FLASK_ENV=production
   SECRET_KEY=tu-clave-super-secreta
   OMDB_API_KEY=c4a84505
   GOOGLE_API_KEY=AIzaSyB8N--E-B7yFzPLAgu0AQ3zL3Mv2Ae7Wbs
   ```
6. Agregar PostgreSQL gratuito
7. ¡Listo! Render importa DATABASE_URI automáticamente

#### Opción B: PYTHONAWHERE (Más simple, sin GitHub)
**Pros:**
- ✅ Interface web intuitiva
- ✅ No necesita Git
- ✅ Panel de control Python
- ✅ Gratuito con limitaciones

**Pasos:**
1. Ir a [pythonanywhere.com](https://pythonanywhere.com)
2. Crear cuenta
3. Subir archivos por SFTP o ZIP
4. Crear Web app con Flask 2.1
5. Configurar WSGI
6. Crear PostgreSQL en "Databases"
7. ¡Listo!

#### Opción C: HEROKU (Pagado, era gratuito)
**Cons:**
- ❌ Plan gratuito descontinuado (era $7/mes plan básico)
- ⚠️ Pero aún tienes 550 dyno-hours/mes gratis con verificación

[Ver instrucciones en DEPLOY.md]

---

### PASO 3️⃣: Migrar la base de datos

#### Si usas SQL (Render/cualquier PostgreSQL):
```powershell
# Ya exportaste con export_sql_dump.py
# En tu panel de control, busca "Ejecutar SQL"
# Copia el contenido de tobucks_export.sql y pega en la consola SQL
```

#### Si usas JSON (más flexible):
```powershell
# El archivo JSON tiene todos tus datos
# Puedes escribir un script para importar según tu BD destino
```

---

### PASO 4️⃣: Preparar Git (para Render/GitHub)

```powershell
# Inicializar repo si no existe
git init

# Ver estado
git status

# Agregar todo (excepto .env y local files por .gitignore)
git add .

# Primer commit
git commit -m "Tobucks: Preparado para producción"

# Crear repo en GitHub.com
# Luego:
git remote add origin https://github.com/TU_USER/tobucks.git
git branch -M main
git push -u origin main
```

---

### PASO 5️⃣: Desplegar en Render (Paso a paso)

1. **Ir a [render.com](https://render.com)** → Sign Up (con GitHub es más fácil)

2. **Dashboard** → "New +" → "Web Service"

3. **Conectar repositorio:**
   - Seleccionar tu repo `Tobucks_Movie_Recommendations_1.1-main`
   - Autorizar si es necesario

4. **Configurar:**
   - Name: `tobucks-app` (lo que quieras)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
   - Instance Type: "Free" (gratis 0.5 GB RAM)

5. **Environment Variables** (Settings → Environment):
   ```
   FLASK_ENV=production
   SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (genera una con openssl rand -hex 32)
   OMDB_API_KEY=c4a84505
   GOOGLE_API_KEY=AIzaSyB8N--E-B7yFzPLAgu0AQ3zL3Mv2Ae7Wbs
   ```

6. **Agregar Base de Datos:**
   - En Render dashboard: "New +" → "PostgreSQL"
   - Crear instancia gratuita
   - Copiar connection string
   - En Web Service, agregar variable:
     ```
     DATABASE_URI=postgresql://user:pass@...
     ```

7. **¡Desplegar!** → "Create Web Service"
   - Render empezará a compilar y desplegar
   - Visit app → ¡Tu sitio estará online en 2-3 minutos!

---

### PASO 6️⃣: Importar datos en la BD de Render

**Opción A: Por consola Render**
1. En el panel de PostgreSQL en Render
2. Ir a "Browser" o "Connection" 
3. Ejecutar el SQL:
```sql
-- Copiar y pegar el contenido de tobucks_export.sql aquí
```

**Opción B: Por consola local**
```powershell
# Descargar el connection string de Render
# Ejecutar (reemplazar con tu string):
psql "postgresql://user:pass@host.render.com:5432/db" < tobucks_export.sql
```

---

## 📸 Arquitectura Final:

```
Internet
   ↓
Render.com (Web Service Python)
   ↓
Tu código Flask (gunicorn)
   ↓
PostgreSQL (base de datos en Render)
```

---

## 🔐 Seguridad - Checklist:

- [ ] ✅ `.env` está en `.gitignore` (nunca subir secretos a GitHub)
- [ ] ✅ `SECRET_KEY` es única y fuerte (usa `openssl rand -hex 32`)
- [ ] ✅ `FLASK_ENV=production` en el servidor
- [ ] ✅ `DEBUG=False` en producción
- [ ] ✅ Variables sensibles en el panel de hosting, NO en código

---

## 🐛 Troubleshooting:

### La app no carga:
```powershell
# Ver logs en Render: Logs tab
# O localmente:
python run.py
```

### Error de BD:
```powershell
# Verificar DATABASE_URI:
# En Render: Settings → Environment
```

### Puerto 5000 en uso:
```powershell
# Cambiar en run.py o usar puerto del servidor
```

---

## 📞 ¿Necesitas ayuda?

1. **Para errores locales**: Ejecuta `python run.py` y ve los logs
2. **Para errores en Render**: Mira la pestaña "Logs" en el panel
3. **Para problemas de BD**: Verifica el connection string

---

## 🎉 ¡Resumido!

```powershell
# 1. Exportar datos
python export_sql_dump.py

# 2. Pushear a GitHub
git add .
git commit -m "Ready for production"
git push origin main

# 3. En Render.com: Conectar repo y desplegar (2-3 mins)

# 4. Importar datos en BD de Render (1-2 mins)

# ¡LISTO! Tu app está online! 🚀
```

---

**Última actualización**: 10 de febrero de 2026
**Stack**: Flask + PostgreSQL + Render
**Costo**: ✅ GRATIS (dentro del plan gratuito de Render)

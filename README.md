# Email Blacklist Microservice

Este microservicio permite registrar y consultar direcciones de correo electrónico en una lista negra global. Está construido con **Flask**, **PostgreSQL**, **Docker** y sigue una arquitectura lista para producción. 

---

## 🧱 Estructura del Proyecto

```
email-blacklist-service/
├── application.py
├── requirements.txt
├── buildspec.yml
├── Dockerfile
├── docker-compose.yml
├── .env
├── config/
│   ├── __init__.py
│   ├── default.py
│   └── production.py
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── blacklist.py
│   ├── schemas/
│   │   └── blacklist_schema.py
│   └── routes/
│       └── blacklist_routes.py
```

---

## 🚀 Endpoints

| Método | Endpoint                    | Descripción                            | Requiere Token |
|--------|-----------------------------|----------------------------------------|----------------|
| POST   | `/blacklists`               | Agrega un correo a la blacklist        | ✅             |
| GET    | `/blacklists/<email>`       | Verifica si un correo está en la lista | ✅             |
| GET    | `/ping`                     | Verifica que el servicio esté vivo     | ❌             |
| POST   | `/reset`                    | Reinicia el estado de la base de datos | ✅             |

---

## 🔐 Token Estático

El microservicio espera un token estático enviado por header:
```
Authorization: Bearer my_static_token
```

Este token debe coincidir con el valor definido en tu archivo `.env`:
```
STATIC_TOKEN=my_static_token
```

---

## ▶️ Uso con Docker

### 1. Construcción y despliegue

```bash
docker-compose down -v
docker-compose up --build
```

### 2. Verifica que los contenedores estén corriendo

```bash
docker ps
```

---

## 🧪 Probar con Postman

### POST /blacklists

**URL:** `http://localhost:5000/blacklists`  
**Método:** POST  
**Headers:**
```
Authorization: Bearer my_static_token
Content-Type: application/json
```

**Body:**
```json
{
  "email": "usuario@example.com",
  "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "blocked_reason": "Comportamiento malicioso"
}
```

---

### GET /blacklists/<email>

**URL:** `http://localhost:5000/blacklists/usuario@example.com`  
**Método:** GET  
**Headers:**  
```
Authorization: Bearer my_static_token
```

---

### GET /ping

```bash
curl http://localhost:5000/ping
```

---

### POST /reset

```bash
curl -X POST http://localhost:5000/reset -H "Authorization: Bearer my_static_token"
```

---

## 🛠 Migraciones de base de datos (dev)

Para aplicar las migraciones y crear las tablas dentro del contenedor:

```bash
docker exec -it blacklist-api flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

---

## ❓ ¿Qué es `runtime.txt`?

Este archivo se usa para plataformas como **Heroku** o **Elastic Beanstalk** para definir la versión de Python que se debe usar:

```txt
python-3.9.13
```

🔺 **No es necesario si estás usando Docker**, puedes borrarlo sin problema. La versión de Python está definida en el `Dockerfile`:

```Dockerfile
FROM python:3.9
```

---

## 🧹 ¿Puedo borrar `.ebextensions`?

Sí. Esta carpeta solo es necesaria si estás desplegando manualmente en **Elastic Beanstalk**. Si estás trabajando solo con Docker local, puedes eliminarla.

---

## 👨‍💻 Autor

Desarrollado como parte del Proyecto 1 - MISO Ingeniería de Software (Uniandes)

---


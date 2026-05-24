# NAYÁ — API

Sistema backend para la gestión de terapeutas y pacientes, construido con **FastAPI** y **PostgreSQL**.

---

## 👥 Integrantes del Equipo

| Nombre | 
|--------|
| Diego Rivera Cisneros |
| Rodrigo Vega Espinoza |
| Eduardo Osvaldo Rodriguez Gutierrez |
| Annatar Armando Murillo Rivera |

---

## 🔐 PoC — OWASP A05: Security Misconfiguration

### Descripción

Esta PoC demuestra la vulnerabilidad **OWASP Top 10 A05:2021 — Security Misconfiguration**, clasificada bajo el **CWE-200: Exposure of Sensitive Information to an Unauthorized Actor**.

Se implementó un endpoint deliberadamente inseguro (`GET /auth/debug-env-poc`) que simula un error no controlado en producción y devuelve información crítica del sistema en la respuesta HTTP, sin requerir ningún tipo de autenticación.

### Endpoint Vulnerable

```
GET /auth/debug-env-poc
```

### Información Expuesta

| Campo en la respuesta | Dato filtrado | Impacto |
|---|---|---|
| `file_exposed` | Ruta absoluta del archivo en el servidor | Revela la estructura interna del contenedor Docker |
| `exposed_db_user` | Usuario de la base de datos (`postgres`) | Facilita ataques dirigidos a la DB |
| `exposed_jwt_secret` | Clave secreta de firma de tokens JWT | Permite forjar tokens y suplantar cualquier usuario |

### Ejemplo de Respuesta Vulnerable

```json
{
  "status": "vulnerable_debug_active",
  "exception_type": "ZeroDivisionError",
  "exception_message": "division by zero",
  "file_exposed": "/app/app/api/auth/auth_router.py",
  "exposed_db_user": "postgres",
  "exposed_jwt_secret": "<clave_secreta_jwt>",
  "remediation": "Desactivar modo DEBUG y usar NayaHttpResponse.internal_error() globalmente."
}
```

### Mitigación

- Nunca exponer detalles de excepciones en respuestas HTTP de producción.
- Usar siempre un manejador de errores genérico (`NayaHttpResponse.internal_error()`).
- Gestionar secretos y credenciales mediante variables de entorno seguras (nunca en el código).
- Eliminar cualquier endpoint de diagnóstico antes de desplegar a producción.
- Implementar un manejador global de errores en FastAPI como red de seguridad adicional.
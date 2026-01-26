# Guía de Despliegue en Render (Dashboard OVA)

Esta guía detalla los pasos para desplegar el Dashboard en la instancia de Render de la empresa.

## 1. Preparación del Repositorio

Asegúrate de que los archivos sensibles NO estén en el repositorio. El archivo `.gitignore` ya ha sido configurado para ignorar:

- `.env`
- `backend/token_cache.bin`
- `backend/token.txt`
- `token.txt`

### Para mover al workspace de la empresa:

Si necesitas cambiar el repositorio remoto a la cuenta de la empresa:

```bash
git remote set-url origin https://github.com/EMPRESA/dashboard-ova.git
git push -u origin main
```

## 2. Configuración en Render

1. Crea un nuevo **Web Service** en Render.
2. Conecta el repositorio de GitHub.
3. Configura los siguientes campos:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

## 3. Variables de Entorno (Environment Variables)

En la sección "Environment" de Render, agrega las siguientes variables. Esto es CRUCIAL para que la conexión con OneDrive funcione sin intervención manual.

| Variable                  | Valor Sugerido / Fuente                              |
| :------------------------ | :--------------------------------------------------- |
| `USE_ONEDRIVE`            | `true`                                               |
| `MICROSOFT_CLIENT_ID`     | _Tu Client ID de Azure_                              |
| `MICROSOFT_CLIENT_SECRET` | _Tu Secret de Azure_                                 |
| `MICROSOFT_TENANT_ID`     | `consumers`                                          |
| `MICROSOFT_DRIVE_ID`      | `4B03C1D355CFB1C4`                                   |
| `EXCEL_VENTAS_ITEM_ID`    | `4B03C1D355CFB1C4!s8e6bb22c8f954004a73aa2cef7b84f1f` |
| `EXCEL_ALMACEN_ITEM_ID`   | `4B03C1D355CFB1C4!s0fee0b03ddee44308be946c94338db39` |
| `MICROSOFT_REFRESH_TOKEN` | _Copia el valor de tu `.env` local_                  |

> **Nota sobre el Refresh Token:** El sistema está diseñado para usar este refresh token para generar nuevos access tokens automáticamente en Render, evitando errores 401.

## 4. Verificación

Una vez desplegado, puedes verificar el estado en:
`https://tu-app.onrender.com/api/health`

Debería retornar `{"status": "ok", "source": "onedrive"}`.

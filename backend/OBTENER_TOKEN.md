# Guía Rápida: Obtener Token de Microsoft Graph

## Opción Más Simple: Graph Explorer

1. Ve a: https://developer.microsoft.com/en-us/graph/graph-explorer

2. Haz clic en **"Sign in to Graph Explorer"**

3. Inicia sesión con: `josellanos.95@hotmail.com`

4. Una vez dentro, en la barra superior verás tu nombre/foto de perfil

5. Haz clic en tu perfil → **"Consent to permissions"** o busca el ícono de engranaje ⚙️

6. Busca y activa estos permisos:
   - `Files.Read`
   - `Files.Read.All`

7. Haz clic en **"Consent"** para autorizar

8. Ahora, en la parte superior, haz clic en **"Access token"** (ícono de llave 🔑)

9. Copia el token completo que aparece

10. Pégalo en el archivo `.env`:

```
MICROSOFT_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJub25jZSI6...
```

11. Reinicia el servidor del dashboard

## Nota Importante

Este token expira en 1 hora. Para producción, necesitaremos implementar refresh token, pero para probar que todo funciona, esto es suficiente.

Una vez que confirmes que funciona con el token manual, implementaremos la renovación automática.

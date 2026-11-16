# Mini-Azure Vision: Sistema Local de Control de Uniforme On-Premise

Sistema de control de ingreso automatizado mediante visión artificial para verificar en tiempo real el uso correcto del uniforme (corbata) en estudiantes. Este proyecto implementa una arquitectura On-Premise (Nube Privada) utilizando microservicios locales para garantizar baja latencia, privacidad de datos y optimización de costos frente a soluciones de nube pública.

## 🏗️ Arquitectura y Tecnologías

El sistema está dividido en una arquitectura Cliente-Servidor comunicada a través de la red de área local (LAN).

- **IA y Modelos:** Ultralytics YOLOv8 (modelo base `yolov8n.pt` para detección de presencia y modelo _fine-tuned_ `best.pt` para clasificación del uniforme).
- **Backend (Servidor):** FastAPI, Uvicorn, Python 3.10.
- **Despliegue:** Docker, Docker Compose.
- **Cliente (Streaming):** OpenCV, Requests (Transmisión de fotogramas en Base64 mediante peticiones HTTP POST).

---

## 🚀 Instalación y Despliegue

### 1. Servidor API REST (Integrante A - Rol Cloud/IA)

El servidor expone los servicios de inferencia empaquetados en un contenedor Docker.

**Requisitos previos:** Docker y Docker Compose instalados.

1. Clonar el repositorio y navegar a la carpeta raíz del proyecto.
2. Asegurarse de que el modelo entrenado (`best.pt`) esté ubicado en `server/model/best.pt`.
3. Configurar las variables en `server/.env`:

```env
BACKEND_PORT=8000
CONTAINER_NAME=mini_azure_server
MODEL_PATH=model/best.pt
CONFIDENCE_THRESHOLD=0.80

```

4. Construir y levantar el contenedor:

```bash
docker compose up -d --build

```

5. Habilitar el tráfico TCP para el puerto `8000` en el Firewall de Windows del servidor.
6. La documentación interactiva (Swagger UI) estará disponible en: `http://localhost:8000/docs` (o la IP local del servidor).

### 2. Script Cliente (Integrante B - Rol Redes)

El cliente captura el video de la cámara web, redimensiona el fotograma para optimizar el ancho de banda y lo transmite al servidor.

**Requisitos previos:** Python 3.10+ y una cámara web conectada.

1. Instalar las dependencias del cliente:

```bash
pip install opencv-python requests

```

2. Editar el archivo `client/client.py` y actualizar la variable `SERVER_URL` con la dirección IP local de la PC Servidor:

```python
SERVER_URL = "http://<IP_DEL_SERVIDOR>:8000/vision/uniforme"

```

3. Ejecutar el sistema de validación:

```bash
python client/client.py

```

_(Presionar la tecla 'q' en la ventana de video para finalizar la transmisión)._

---

## 📡 Endpoints de la API

- `POST /vision/general`: Recibe un fotograma en Base64. Utiliza YOLOv8 preentrenado (`yolov8n.pt`) para detectar si existe una persona en la escena. Retorna un booleano.
- `POST /vision/uniforme`: Recibe un fotograma en Base64. Utiliza el modelo entrenado (`best.pt`) para clasificar si el estudiante porta correctamente la corbata.
- **Respuesta Exitosa (Ejemplo):**

```json
{
  "estado": "con_corbata",
  "confianza": 0.95,
  "acceso": "PERMITIDO"
}
```

- _Nota:_ Si la confianza es menor al 80% (0.80) o no se detecta la corbata, el campo `acceso` retornará `"DENEGADO"` y el estado se forzará a `"sin_corbata"`.

---

## 📊 Análisis Técnico: On-Premise vs Nube Pública

| Criterio Técnico              | Despliegue Local (On-Premise / Edge AI)                                                                                               | Servicio en Nube Pública (Ej. Azure AI Vision)                                                                                       |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Privacidad y Seguridad**    | **Ventaja:** Los fotogramas y rostros de los estudiantes no salen de la red LAN, garantizando la privacidad absoluta.                 | **Desventaja:** Las imágenes deben viajar por internet hacia servidores externos (terceros).                                         |
| **Latencia y Disponibilidad** | **Ventaja:** Tiempo de respuesta ultrabajo (inferencia local en ms) y total independencia del servicio de internet de la institución. | **Desventaja:** Dependencia total del ancho de banda y riesgo de _lag_ o caídas si el internet falla.                                |
| **Costos Operativos**         | **Ventaja:** Costo marginal cero por transacción o inferencia. Escalabilidad limitada solo por el hardware del servidor local.        | **Desventaja:** Modelo de pago por uso (_Pay-as-you-go_). Un alto volumen de estudiantes genera un costo mensual recurrente elevado. |

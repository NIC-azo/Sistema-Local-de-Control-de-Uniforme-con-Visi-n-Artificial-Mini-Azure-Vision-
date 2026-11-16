import cv2
import requests
import base64
import time
import json

# IMPORTANTE: Reemplaza esto con la IP local (IPv4) de la PC Servidor si estás en otra PC.
# Si el cliente y el servidor corren en la misma PC (Antigravity IDE), deja localhost.
SERVER_URL = "http://localhost:8000/vision/uniforme"

def image_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_b64}"

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se puede acceder a la cámara web.")
        return

    print("Iniciando transmisión al servidor On-Premise...")
    print("Presiona 'q' en la ventana de video para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Reducir resolución para menor latencia en la red LAN
        frame_resized = cv2.resize(frame, (640, 480))
        
        # Preparar payload JSON
        payload = {
            "image": image_to_base64(frame_resized),
            "client_timestamp": time.time()
        }

        try:
            # Petición HTTP POST al servidor local
            start_time = time.time()
            response = requests.post(SERVER_URL, json=payload, timeout=2.0)
            latency = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                estado = data.get("estado", "Desconocido")
                confianza = data.get("confianza", 0.0)
                acceso = data.get("acceso", "DENEGADO")

                # Lógica de colores e interfaz
                color = (0, 255, 0) if acceso == "PERMITIDO" else (0, 0, 255)
                
                cv2.rectangle(frame_resized, (10, 10), (630, 80), color, -1)
                cv2.putText(frame_resized, f"ACCESO {acceso} - {estado.upper()}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame_resized, f"Confianza: {confianza*100:.1f}% | Latencia: {latency}ms", (20, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        except requests.exceptions.RequestException as e:
            cv2.putText(frame_resized, "Servidor No Alcanzable (Check LAN)", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Renderizar fotograma
        cv2.imshow("Mini-Azure Vision: Control de Uniforme", frame_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
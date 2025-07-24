
from flask import Flask, request, jsonify
import base64
import json
import paho.mqtt.client as mqtt
import ssl

app = Flask(__name__)

# ✅ MQTT Configuration
MQTT_BROKER = "e3b73ee9a52a44a0837e55b8c438ba5a.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "Test35"
MQTT_PASSWORD = "Ab123456"
MQTT_TOPIC = "images/uploaded"

def publish_to_mqtt(image_base64, filename):
    try:
        # ✅ สร้าง client + Auth
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # ✅ เปิด TLS (สำคัญมากกับ HiveMQ Cloud)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

        # ✅ เชื่อมต่อ HiveMQ
        client.connect(MQTT_BROKER, MQTT_PORT)

        # ✅ สร้าง payload JSON
        payload = {
            "filename": filename,
            "image_base64": image_base64
        }

        # ✅ ส่งข้อความขึ้น topic
        result = client.publish(MQTT_TOPIC, json.dumps(payload))

        # ✅ เช็กผลลัพธ์
        if result.rc == 0:
            print("✅ Published to MQTT successfully.")
        else:
            print(f"❌ Failed to publish. Result code: {result.rc}")

        client.disconnect()
    except Exception as e:
        print(f"❌ Error publishing to MQTT: {e}")

@app.route("/upload-image", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()
        image_base64 = data.get("image_base64")
        filename = data.get("filename", "image.jpg")

        if not image_base64:
            return jsonify({"error": "Missing image_base64"}), 400

        publish_to_mqtt(image_base64, filename)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"❌ Error in upload_image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

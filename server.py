from flask import Flask, request, jsonify
import base64
import json
import paho.mqtt.client as mqtt
import ssl

app = Flask(__name__)

# ✅ MQTT Broker Config (HiveMQ Cloud)
MQTT_BROKER = "e3b73ee9a52a44a0837e55b8c438ba5a.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "Test35"
MQTT_PASSWORD = "Ab123456"
MQTT_TOPIC = "images/uploaded"

def publish_to_mqtt(image_base64, filename):
    try:
        print("📤 Connecting to MQTT broker...")
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        client.connect(MQTT_BROKER, MQTT_PORT)
        print("✅ Connected to MQTT")

        payload = {
            "filename": filename,
            "image_base64": image_base64
        }

        result = client.publish(MQTT_TOPIC, json.dumps(payload))

        if result.rc == 0:
            print("✅ Published to MQTT successfully.")
        else:
            print(f"❌ Failed to publish. Result code: {result.rc}")

        client.disconnect()
        print("🔌 Disconnected from MQTT.")

    except Exception as e:
        print(f"❌ Error publishing to MQTT: {e}")

@app.route("/upload-image", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()
        print("📥 Received POST /upload-image")
        print("🔎 Payload keys:", list(data.keys()))

        image_base64 = data.get("image_base64")
        filename = data.get("filename", "image.jpg")

        if not image_base64:
            print("❌ Missing image_base64 in payload")
            return jsonify({"error": "Missing image_base64"}), 400

        print(f"📤 Publishing filename: {filename}")
        publish_to_mqtt(image_base64, filename)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"❌ Error in upload_image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting Flask MQTT Image Uploader...")
    app.run(host="0.0.0.0", port=5000)

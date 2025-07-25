from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
import base64
import os

app = Flask(__name__)

# ==== HiveMQ Cloud Credentials ====
broker = "efff4f0d50144b6d92ab49737f0971b7.s1.eu.hivemq.cloud"
port = 8883
username = "Test35"
password = "Ab123456"
topic = "test/image"

# ==== MQTT Setup ====
def setup_mqtt():
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.connect(broker, port)
    return client

# ==== Encode image to base64 ====
def encode_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ==== API Endpoint ====
@app.route("/send-image", methods=["POST"])
def send_image():
    data = request.json
    image_path = data.get("image_path")

    if not image_path or not os.path.isfile(image_path):
        return jsonify({"error": "Invalid or missing image_path"}), 400

    try:
        encoded = encode_image(image_path)
        client = setup_mqtt()
        info = client.publish(topic, encoded, retain=True)
        info.wait_for_publish()
        client.disconnect()

        if info.is_published():
            return jsonify({"message": "✅ Image sent via MQTT"}), 200
        else:
            return jsonify({"error": "❌ Failed to publish"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==== Run Flask ====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

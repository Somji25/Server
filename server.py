# === sender.py ===
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
import json
import time

app = Flask(__name__)

broker = "efff4f0d50144b6d92ab49737f0971b7.s1.eu.hivemq.cloud"
port = 8883
username = "Test35"
password = "Ab123456"
topic = "test/12"

client = mqtt.Client()
client.username_pw_set(username, password)

client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to HiveMQ Broker")
    else:
        print(f"❌ Connection failed with code {rc}")

client.on_connect = on_connect
client.connect(broker, port)
client.loop_start()
time.sleep(2)  # wait for connect

# In-memory index tracking per session (simple, one user)
images_received = 0
total_expected = 0

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global images_received, total_expected
    data = request.get_json()

    if not data or 'image_base64' not in data:
        return jsonify({'error': 'Missing image_base64'}), 400

    image_base64 = data['image_base64']
    total_images = data.get('total_images', 1)
    reset = data.get('reset', False)

    if reset or total_images != total_expected:
        images_received = 0
        total_expected = total_images

    images_received += 1

    mqtt_payload = {
        "image_base64": image_base64,
        "index": images_received,
        "total_images": total_images
    }

    json_payload = json.dumps(mqtt_payload)
    info = client.publish(topic, json_payload)
    info.wait_for_publish()

    if info.is_published():
        return jsonify({
            'message': '✅ Image published to MQTT',
            'index': images_received,
            'total': total_images
        }), 200
    else:
        return jsonify({'message': '❌ Failed to publish image'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

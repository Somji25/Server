from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
import base64

app = Flask(__name__)

# ==== HiveMQ Cloud Credentials ====
broker = "efff4f0d50144b6d92ab49737f0971b7.s1.eu.hivemq.cloud"
port = 8883
username = "Test35"
password = "Ab123456"
topic = "test/12"

# ==== MQTT Setup ====
client = mqtt.Client()
client.username_pw_set(username, password)
client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to HiveMQ Broker")
        else:
            print(f"❌ Connection failed with code {rc}")

    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()

# ==== Flask route to receive image ====
@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()

    if not data or 'image_base64' not in data:
        return jsonify({"error": "Missing image_base64"}), 400

    image_base64 = data['image_base64']

    # ==== Connect and publish to MQTT ====
    connect_mqtt()
    
    info = client.publish(topic, image_base64, retain=True)
    info.wait_for_publish()
    
    client.loop_stop()
    client.disconnect()

    if info.is_published():
        return jsonify({"message": "✅ Image published successfully"}), 200
    else:
        return jsonify({"message": "❌ Failed to publish"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

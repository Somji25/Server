from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
import time

app = Flask(__name__)

# HiveMQ Cloud Credentials
broker = "efff4f0d50144b6d92ab49737f0971b7.s1.eu.hivemq.cloud"
port = 8883
username = "Test35"
password = "Ab123456"
topic = "test/12"

# MQTT Setup
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
time.sleep(2)

# ตัวแปรเก็บจำนวนภาพที่ส่งไปแล้ว (ในหน่วยความจำเซิร์ฟเวอร์)
images_received = 0

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global images_received
    data = request.get_json()

    if not data or 'image_base64' not in data:
        return jsonify({'error': 'Missing image_base64'}), 400

    image_base64 = data['image_base64']
    total_images = data.get('total_images')  # จำนวนภาพทั้งหมดที่ Power Apps ตั้งใจจะส่ง

    images_received += 1  # เพิ่มจำนวนที่รับไว้แล้ว

    print(f"[{time.strftime('%H:%M:%S')}] Received base64 (preview):", image_base64[:50])

    # ส่งภาพไปยัง MQTT
    info = client.publish(topic, image_base64)
    info.wait_for_publish()

    if info.is_published():
        response = {
            'message': '✅ Image published to MQTT',
            'image_index': images_received,
            'total_expected': total_images
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': '❌ Failed to publish image'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

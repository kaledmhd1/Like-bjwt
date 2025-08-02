from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

executor = ThreadPoolExecutor(max_workers=100)

def Encrypt_ID(x):
    x = int(x)
    dec = ['{:x}'.format(i + 128) for i in range(128)]
    xxx = ['{:x}'.format(i) for i in range(1, 128)]
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                y = (x - int(x)) * 128
                z = (y - int(y)) * 128
                n = (z - int(z)) * 128
                m = (n - int(n)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                y = (x - int(x)) * 128
                z = (y - int(y)) * 128
                n = (z - int(z)) * 128
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def process_like(player_id, token):
    encrypted_id = Encrypt_ID(player_id)
    encrypted_api = encrypt_api(f"08{encrypted_id}1007")
    TARGET = bytes.fromhex(encrypted_api)

    url = "https://clientbp.ggblueshark.com/LikeProfile"
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB50',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    with httpx.Client(verify=False) as client:
        response = client.post(url, headers=headers, data=TARGET)

    return response.status_code == 200

def like_task(player_id, token):
    try:
        return process_like(player_id, token)
    except Exception:
        return False

@app.route("/send_like", methods=["GET"])
def send_like():
    player_id = request.args.get("player_id")
    token = request.args.get("token")

    if not player_id or not token:
        return jsonify({"status": "failed"}), 200

    try:
        player_id = int(player_id)
    except ValueError:
        return jsonify({"status": "failed"}), 200

    future = executor.submit(like_task, player_id, token)
    success = future.result()

    return jsonify({"status": "success" if success else "failed"}), 200

# هذا هو handler الذي تستخدمه Vercel
def handler(environ, start_response):
    return app(environ, start_response)

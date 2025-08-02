from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

executor = ThreadPoolExecutor(max_workers=100)

def Encrypt_ID(x):
    x = int(x)
    dec = ['{:x}'.format(i + 128) for i in range(128)]
    xxx = ['{:x}'.format(i) for i in range(1, 128)]
    x_div = x / 128

    if x_div > 128:
        x_div = x_div / 128
        if x_div > 128:
            x_div = x_div / 128
            if x_div > 128:
                x_div = x_div / 128
                y = (x_div - int(x_div)) * 128
                z = (y - int(y)) * 128
                n = (z - int(z)) * 128
                m = (n - int(n)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x_div)]
            else:
                y = (x_div - int(x_div)) * 128
                z = (y - int(y)) * 128
                n = (z - int(z)) * 128
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x_div)]
        else:
            # حالة x_div أقل أو يساوي 128
            y = (x_div - int(x_div)) * 128
            z = (y - int(y)) * 128
            return dec[int(z)] + dec[int(y)] + xxx[int(x_div)]
    else:
        # حالة x أقل أو يساوي 128 (أصلًا)
        return xxx[int(x_div)]  # تأكد أنه صحيح حسب المنطق عندك

def encrypt_api(plain_text):
    # نص الـ plain_text المفترض يكون hex string
    plain_bytes = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_bytes, AES.block_size))
    return cipher_text.hex()

def process_like(player_id, token):
    encrypted_id = Encrypt_ID(player_id)
    # نكون نص hex كامل نضيف 08 وباقي الأرقام
    plain_hex = f"08{encrypted_id}1007"
    encrypted_api = encrypt_api(plain_hex)

    url = "https://clientbp.ggblueshark.com/LikeProfile"
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB50',
        # أغير الـ Content-Type لأنه نرسل بيانات ثنائية
        'Content-Type': 'application/octet-stream',
    }

    # بيانات body تكون بايت من hex النص المشفر
    data_bytes = bytes.fromhex(encrypted_api)

    with httpx.Client(verify=False) as client:
        response = client.post(url, headers=headers, data=data_bytes)

    return response.status_code == 200

def like_task(player_id, token):
    try:
        return process_like(player_id, token)
    except Exception as e:
        print(f"Error in like_task: {e}")
        return False

@app.route("/send_like", methods=["GET"])
def send_like():
    player_id = request.args.get("player_id")
    token = request.args.get("token")

    if not player_id or not token:
        return jsonify({"status": "failed", "reason": "Missing parameters"}), 400

    try:
        player_id_int = int(player_id)
    except ValueError:
        return jsonify({"status": "failed", "reason": "Invalid player_id"}), 400

    future = executor.submit(like_task, player_id_int, token)
    success = future.result()

    return jsonify({"status": "success" if success else "failed"}), 200

# handler لو انت فعلاً تحتاجه لـ Vercel
def handler(environ, start_response):
    return app(environ, start_response)

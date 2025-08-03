from flask import Flask, request, jsonify
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor
import json
import base64

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=40)

def Encrypt_ID(x):
    x = int(x)
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f']
    hex_str = hex(x)[2:]
    hex_str = hex_str.zfill(16)
    encrypted = ''.join(dec[int(c, 16)] for c in hex_str)
    return encrypted

def GET_PAYLOAD_BY_DATA(jwt_token):
    try:
        payload_part = jwt_token.split('.')[1]
        payload_part += '=' * (-len(payload_part) % 4)  # Padding for base64
        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(decoded_bytes)
        return payload
    except Exception as e:
        return {}

def send_like(token, uid):
    try:
        payload = GET_PAYLOAD_BY_DATA(token)
        encrypted_uid = Encrypt_ID(uid)
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://like-api-bngxa.onrender.com/like?id={encrypted_uid}"
        res = httpx.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            return {"token_id": payload.get("account_id"), "nickname": payload.get("nickname"), "status": "success", "target_uid": uid}
        elif res.status_code == 400:
            try:
                detail = res.json().get("detail", "").lower()
                if "limit" in detail or "like" in detail or "daily" in detail:
                    print(f"✅ الحساب {payload.get('nickname')} (ID: {payload.get('account_id')}) وصل الحد اليومي عند محاولة لايك لـ UID {uid}")
                    return {"token_id": payload.get("account_id"), "nickname": payload.get("nickname"), "status": "limit_reached", "target_uid": uid}
            except:
                pass
        return {"token_id": payload.get("account_id"), "nickname": payload.get("nickname"), "status": "failed", "target_uid": uid}
    except Exception as e:
        return {"token_id": None, "nickname": None, "status": "error", "target_uid": uid}

@app.route('/send_like')
def handle_like():
    token = request.args.get('token')
    uid = request.args.get('id')
    if not token or not uid:
        return jsonify({"error": "Missing token or id"}), 400

    future = executor.submit(send_like, token, uid)
    result = future.result()

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

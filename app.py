from flask import Flask, request, jsonify
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

app = Flask(__name__)

def Encrypt_ID(x):
    x = int(x)
    dec = [...]  # نفس محتوى dec
    xxx = [...]  # نفس محتوى xxx
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
    strx = int(x)
    y = (x - int(strx)) * 128
    stry = str(int(y))
    z = (y - int(stry)) * 128
    strz = str(int(z))
    n = (z - int(strz)) * 128
    strn = str(int(n))
    return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def handle_like(uid, token):
    try:
        encrypted_id = Encrypt_ID(uid)
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

        with httpx.Client(verify=False, timeout=10) as client:
            response = client.post(url, headers=headers, data=TARGET)

        if response.status_code == 200:
            return {"status": "success"}
        elif response.status_code == 500 and "daily" in response.text.lower():
            return {"status": "daily_limit"}
        else:
            return {"status": "failed", "reason": response.text}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

@app.route("/send_like", methods=["GET"])
def send_like():
    uid = request.args.get("uid")
    token = request.args.get("token")

    if not uid or not token:
        return jsonify({"error": "uid and token are required in query params"}), 400

    try:
        uid = int(uid)
    except ValueError:
        return jsonify({"error": "uid must be an integer"}), 400

    result = handle_like(uid, token)

    if result["status"] == "success":
        return jsonify({
            "success": 1,
            "daily_limit": 0,
            "daily_limit_uids": []
        }), 200
    elif result["status"] == "daily_limit":
        return jsonify({
            "success": 0,
            "daily_limit": 1,
            "daily_limit_uids": [uid]
        }), 200
    else:
        return jsonify({
            "success": 0,
            "daily_limit": 0,
            "daily_limit_uids": [],
            "error": result.get("reason", "Unknown error")
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

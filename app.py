
import os, base64, zlib, json
from flask import Flask, render_template, request, send_file, flash
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = "pixelcoder-secret"

def encode_image(img):
    w, h = img.size
    rgba = img.convert("RGBA").tobytes()
    compressed = zlib.compress(rgba, 9)
    payload = {"w": w, "h": h, "data": base64.b64encode(compressed).decode()}
    return json.dumps(payload).encode()

def decode_image(encoded_bytes):
    obj = json.loads(encoded_bytes.decode())
    w, h = obj["w"], obj["h"]
    compressed = base64.b64decode(obj["data"])
    rgba = zlib.decompress(compressed)
    img = Image.frombytes("RGBA", (w, h), rgba)
    return img

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode_route():
    file = request.files.get("image")
    if not file:
        flash("Upload an image first.")
        return render_template("index.html")
    img = Image.open(file)
    encoded = encode_image(img)
    buf = BytesIO(); buf.write(encoded); buf.seek(0)
    return send_file(buf, mimetype="application/json", as_attachment=True, download_name="encoded.pcd")

@app.route("/decode", methods=["POST"])
def decode_route():
    file = request.files.get("codefile")
    if not file:
        flash("Upload a .pcd file first.")
        return render_template("index.html")
    try:
        data = file.read()
        img = decode_image(data)
    except:
        flash("Invalid or corrupted .pcd file.")
        return render_template("index.html")

    buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=True, download_name="decoded.png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

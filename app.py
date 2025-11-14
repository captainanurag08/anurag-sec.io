
import os, json, base64, zlib
from flask import Flask, render_template, request, send_file, flash
from PIL import Image
from io import BytesIO

app=Flask(__name__)
app.secret_key="xyz123"

def encode_image(img):
    px=list(img.getdata())
    w,h=img.size
    raw=json.dumps({"w":w,"h":h,"px":px}).encode()
    comp=zlib.compress(raw,9)
    return base64.b64encode(comp)

def decode_image(data):
    comp=base64.b64decode(data)
    raw=zlib.decompress(comp)
    obj=json.loads(raw.decode())
    w,h=obj["w"],obj["h"]
    img=Image.new("RGB",(w,h))
    img.putdata([tuple(p) for p in obj["px"]])
    return img

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encode",methods=["POST"])
def encode_route():
    file=request.files.get("image")
    if not file:
        flash("No image uploaded"); return render_template("index.html")
    img=Image.open(file).convert("RGB")
    data=encode_image(img)
    buf=BytesIO(); buf.write(data); buf.seek(0)
    return send_file(buf,mimetype="text/plain",as_attachment=True,download_name="encoded.txt")

@app.route("/decode",methods=["POST"])
def decode_route():
    file=request.files.get("codefile")
    if not file:
        flash("No file uploaded"); return render_template("index.html")
    try:
        data=file.read()
        img=decode_image(data)
    except:
        flash("Corrupted codefile"); return render_template("index.html")
    buf=BytesIO(); img.save(buf,format="PNG"); buf.seek(0)
    return send_file(buf,mimetype="image/png",as_attachment=True,download_name="decoded.png")

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)

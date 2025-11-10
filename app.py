from flask import Flask, request, jsonify, render_template
import os
from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess
from datetime import datetime

## Add required imports
CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
CONTAINER_NAME = os.environ.get("IMAGES_CONTAINER", "images-demo")


bsc = BlobServiceClient.from_connection_string(CONNECTION_STRING)
cc  = bsc.get_container_client(CONTAINER_NAME) # Replace with Container name cc.url will get you the url path to the container.  
app = Flask(__name__)
@app.get("/")
def index():
    return render_template("index.html")
@app.post("/api/v1/upload")
def upload():
    f = request.files["file"]
    filename = f.filename
    print(filename)
    try:
        img_blob = f"{datetime.utcnow().strftime("%Y%m%dT%H%M%S")}-{filename}"
        img_bc = bsc.get_blob_client(CONTAINER_NAME, img_blob)
        img_bc.upload_blob(f.stream, overwrite=True, content_settings=ContentSettings(content_type="image/jpeg"))
    except Exception as e:
        print(e)
        return jsonify(ok=False, error=str(e)), 500
    return jsonify(ok=True, url=f"{cc.url}/{f.filename}")
    # Complete this section so that you can uplaod files
@app.get("/api/v1/gallery")
def gallery():
    urls = [f"{cc.url}/{b.name}" for b in cc.list_blobs()]
    return jsonify(ok=True, gallery=urls)

@app.get("/api/v1/health")
def health():
    return jsonify(ok=True, container=cc.container_name)
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)

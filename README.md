# Image Uploader Flask App
A super simple image uploader. Takes either an image file or url and saves it to server, and serves it back on this CORS friendly server.

Stores up to 500 images, then starts to cull them.

## Install

```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements

# create uploads folder
mkdir uploads
```

## Run

Runs at http://0.0.0.0:5000

```
python main.py
```

## API (CURL examples)

### Upload by file

```
curl http://0.0.0.0:5000/upload/file  -F file=@example.png   -X POST

{"new_url": "http://0.0.0.0:5000/get/example.png", "success": "true"}
```

### Upload by URL

Filename is the hashed URL for the image

```
curl http://0.0.0.0:5000/upload/url --data url="https://c1.staticflickr.com/1/764/22721826666_f874599d8f_k.jpg"

{"new_url": "http://0.0.0.0:5000/get/e8881593e82109cdd89341ad82a2c9ee.jpg", "success": "true"}
```
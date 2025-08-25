from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageEnhance, ImageOps
import io
import os
import uuid

app = Flask(__name__, static_folder='.', static_url_path='')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        file     = request.files['image']
        fmt      = request.form.get('format', 'jpeg').lower()
        quality  = int(request.form.get('quality', 90))
        width    = int(request.form.get('width')) if request.form.get('width') else None
        filter_  = request.form.get('filter', 'none')

        # Pillow only supports JPEG, PNG, WebP, GIF
        if fmt not in {'jpeg', 'png', 'webp', 'gif'}:
            fmt = 'jpeg'

        img = Image.open(file.stream).convert('RGB')

        # Resize
        if width:
            w, h = img.size
            height = int(h * width / w)
            img = img.resize((width, height), Image.LANCZOS)

        # Filters
        if filter_ == 'grayscale':
            img = img.convert('L').convert('RGB')
        elif filter_ == 'sepia':
            sepia = Image.new('RGB', img.size, (112, 66, 20))
            img = Image.blend(img.convert('RGB'), sepia, 0.5)
        elif filter_ == 'vintage':
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.7)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
        elif filter_ == 'brighten':
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
        elif filter_ == 'invert':
            img = ImageEnhance.Color(img).enhance(0)
            img = ImageOps.invert(img)

        # Save to buffer
        buffer = io.BytesIO()
        save_kwargs = {'quality': quality} if fmt == 'jpeg' else {}
        img.save(buffer, format=fmt.upper(), **save_kwargs)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype=f'image/{fmt}',
            as_attachment=True,
            download_name=f'converted.{fmt}'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

import os
import tempfile
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract

app = Flask(__name__)

def extract_text_as_lines(image_path, psm=6):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        image = Image.open(image_path)
        
        # Set the PSM mode
        custom_config = f'--psm {psm}'
        raw_text = pytesseract.image_to_string(image, config=custom_config)
        
        # Split the text into lines and filter out empty lines
        lines = [line for line in raw_text.splitlines() if line.strip()]

        return lines

    except FileNotFoundError as fnf_error:
        app.logger.error(fnf_error)
        return []
    except Exception as e:
        app.logger.error(f"Error extracting text from image: {e}")
        return []

@app.route('/')
def home():
    return "Welcome to the OCR API. Use the /extract-text endpoint to upload an image and extract text."

@app.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image = request.files['image']
        
        # Get the psm value from the request, default to 3 if not provided
        psm = request.form.get('psm', default=6, type=int)
        
        # Use tempfile to create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            image_path = temp.name
            image.save(image_path)

        lines = extract_text_as_lines(image_path, psm)

        # Remove the temporary file after processing
        os.remove(image_path)

        if lines:
            return jsonify({"lines": lines})
        else:
            return jsonify({"error": "No text extracted"}), 500
    except Exception as e:
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4001, debug=True)

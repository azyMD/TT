import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import subprocess
import openai

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_audio(input_path, output_path):
    subprocess.run([
        'ffmpeg', '-i', input_path, '-vn', '-acodec', 'mp3', output_path
    ], check=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    file = request.files['file']
    language = request.form.get('language', '').strip()

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    audio_path = filepath
    if not filepath.endswith('.mp3'):
        audio_path = filepath + '.mp3'
        extract_audio(filepath, audio_path)

    try:
        transcription = openai.Audio.transcribe(
            model="whisper-1",
            file=open(audio_path, 'rb'),
            language=language if language else None
        )
        raw_text = transcription['text']

        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Check this transcript for meaningful errors. If everything is fine, reply only: 'Text is OK'. If there are issues, propose an improved version:\n\n{raw_text}"}
            ]
        )
        result = gpt_response['choices'][0]['message']['content']

        return jsonify({
            'original': raw_text,
            'review': result
        })

    finally:
        # Cleanup uploaded and generated files
        try:
            os.remove(filepath)
            if os.path.exists(audio_path) and audio_path != filepath:
                os.remove(audio_path)
        except Exception as e:
            print(f"Cleanup failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

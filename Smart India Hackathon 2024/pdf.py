import os
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from flask import Flask, request, render_template, send_from_directory
import fitz  # PyMuPDF
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['OUTPUT_FOLDER'] = 'static/output/'

# Ensure the upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# PDF Translation Functions
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(pdf_file) as pdf_document:
        for page in pdf_document:
            text += page.get_text()
    return text

def translate_text(text, target_language='hi'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

def create_pdf_with_translated_text(translated_text, output_pdf_file):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(output_pdf_file, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)

    lines = translated_text.splitlines()
    y_position = letter[1] - 40
    line_height = 14

    for line in lines:
        if y_position < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = letter[1] - 40
        c.drawString(40, y_position, line)
        y_position -= line_height

    c.save()

# Video Translation Functions
def extract_audio(video_file):
    video = mp.VideoFileClip(video_file)
    audio_file = os.path.join(app.config['OUTPUT_FOLDER'], "audio.wav")
    video.audio.write_audiofile(audio_file)
    return audio_file

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(audio_file)
    
    with audio as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio_data)
    except sr.RequestError as e:
        logging.error(f"Could not request results from the recognition service; {e}")
        return "Error: Could not request results from the recognition service."
    except sr.UnknownValueError:
        logging.error("Could not understand audio")
        return "Error: Could not understand audio."

def text_to_speech(text, lang='hi', output_file='translated_audio.mp3'):
    tts = gTTS(text=text, lang=lang)
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_file)
    tts.save(output_path)
    return output_path

def combine_audio_with_video(video_file, audio_file):
    video = mp.VideoFileClip(video_file)
    audio = mp.AudioFileClip(audio_file)
    final_video_file = os.path.join(app.config['OUTPUT_FOLDER'], "translated_video.mp4")
    final_video = video.set_audio(audio)
    final_video.write_videofile(final_video_file, codec='libx264')
    return final_video_file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf_translate', methods=['GET', 'POST'])
def pdf_translate():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        text = extract_text_from_pdf(pdf_path)
        translated_text = translate_text(text, 'hi')
        output_pdf_file = os.path.join(app.config['OUTPUT_FOLDER'], "translated_document.pdf")
        create_pdf_with_translated_text(translated_text, output_pdf_file)

        return send_from_directory(app.config['OUTPUT_FOLDER'], "translated_document.pdf", as_attachment=True)

    return render_template('pdf_translate.html')

@app.route('/video_translate', methods=['GET', 'POST'])
def video_translate():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)

        audio_file = extract_audio(video_path)
        text = transcribe_audio(audio_file)

        # Check if transcribing returned an error
        if "Error:" in text:
            return text, 500  # Handle transcription error gracefully

        translated_text = translate_text(text, 'hi')
        translated_audio_file = text_to_speech(translated_text, 'hi')
        final_video_file = combine_audio_with_video(video_path, translated_audio_file)

        return send_from_directory(app.config['OUTPUT_FOLDER'], "translated_video.mp4", as_attachment=True)

    return render_template('video_translate.html')

if __name__ == '__main__':
    app.run(debug=True)

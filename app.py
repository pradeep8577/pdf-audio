from flask import Flask, render_template, request, send_file
import PyPDF2
from bs4 import BeautifulSoup
import os
import requests
import pyttsx3
import uuid
from docx import Document

app = Flask(__name__)

# Define a folder to store generated audio files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def landing_page():
    return render_template('index.html')

# @app.route('/mainpage', methods=['GET'])
# def main_page():
#     return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_pdf():
    text = ''
# file input 
    if 'input_file' in request.files:
      input_file = request.files['input_file']
      if input_file.filename != '':
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], input_file.filename)
            input_file.save(file_path)
           
            file_extension = input_file.filename.rsplit('.', 1)[1].lower()

            text = ''
            if file_extension == 'pdf':
                pdf = PyPDF2.PdfReader(file_path)
                for page in pdf.pages:
                   text += page.extract_text()
            elif file_extension == 'docx':
                doc = Document(file_path)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])


    # Check if the user provided a URL
    if 'url' in request.form:
         url = request.form['url']
         if url:
            try:
                # Fetch text from the URL using requests.
                response = requests.get(url)
                response.raise_for_status()  # Check for a successful response status.

                # Parse the HTML content using BeautifulSoup to extract visible text.
                soup = BeautifulSoup(response.text, 'html.parser')
                visible_text = ' '.join([p.get_text() for p in soup.find_all('p')])

                text += visible_text

            except requests.exceptions.RequestException as e:
                print("Error:", e)

    # Process text-to-speech conversion based on user input (gender and speed)
    gender = request.form['voice']
    speedV = request.form['speed']

    print("Voice Gender:", gender)
    print("Playback Speed:", speedV)

    # Initialize the text-to-speech engine
    audio = pyttsx3.init()
    voices = audio.getProperty('voices')

    if gender == 'Male':
        male_voice = None
        for voice in voices:
            if "David" in voice.name: 
                male_voice = voice
                break

        if male_voice is not None:
            audio.setProperty('voice', male_voice.id) 
        else:
            print("Male voice not found.")

    elif gender == 'Female':
        female_voice = None
        for voice in voices:
            if "Zira" in voice.name:  
                female_voice = voice
                break

        if female_voice is not None:
            audio.setProperty('voice', female_voice.id)  
        else:
            print("Female voice not found.")
  
    if speedV == '1x':
        audio.setProperty('rate', 200)  
    elif speedV == '0.5x':
        audio.setProperty('rate', 100) 
    elif speedV == '2x':
        audio.setProperty('rate', 400)  
    else:
        audio.setProperty('rate', 200)  

    unique_filename = str(uuid.uuid4()) + '.mp3'
    audio.save_to_file(text, os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
    audio.runAndWait()

    return render_template('index.html', audio_filename=unique_filename)

@app.route('/download_audio/<audio_filename>', methods=['GET'])
def download_audio(audio_filename):
    # Return the audio file for download
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename), as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

   
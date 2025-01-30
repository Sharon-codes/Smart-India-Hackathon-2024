import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment

# Step 1: Extract Audio from Video
def extract_audio(video_file):
    video = mp.VideoFileClip(video_file)
    audio = video.audio
    audio_file = "audio.wav"
    audio.write_audiofile(audio_file)
    return audio_file

# Step 2: Transcribe Audio to Text
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(audio_file)
    with audio as source:
        audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text

# Step 3: Translate Text
def translate_text(text, target_language='es'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Step 4: Convert Text to Speech
def text_to_speech(text, lang='es', output_file='translated_audio.mp3'):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)
    return output_file

# Step 5: Combine Translated Audio with Video
def combine_audio_with_video(video_file, audio_file):
    video = mp.VideoFileClip(video_file)
    audio = mp.AudioFileClip(audio_file)
    final_video = video.set_audio(audio)
    final_video_file = "translated_video.mp4"
    final_video.write_videofile(final_video_file, codec='libx264')
    return final_video_file

def main(video_file, target_language='hi'):
    print("Extracting audio from video...")
    audio_file = extract_audio(video_file)
    
    print("Transcribing audio...")
    text = transcribe_audio(audio_file)
    
    print("Translating text...")
    translated_text = translate_text(text, target_language)
    
    print("Converting text to speech...")
    translated_audio_file = text_to_speech(translated_text, target_language)
    
    print("Combining translated audio with video...")
    final_video_file = combine_audio_with_video(video_file, translated_audio_file)
    
    print(f"Process completed. Final video saved as {final_video_file}")

# Example usage
if __name__ == "__main__":
    video_file = ""  # Replace with your video file path
    main(video_file, target_language='hi')  # Translate to Spanish

import whisper
import tempfile

model = whisper.load_model("small")

def transcribe_audio(audio_file):
    # audio_file is a file-like object (e.g. from Streamlit's audio_input)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path)
    return result["text"]
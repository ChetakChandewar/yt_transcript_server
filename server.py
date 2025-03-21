import os
import subprocess
import webvtt
from flask import Flask, request, jsonify
from flask_cors import CORS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

def download_subtitles(video_url):
    command = [
        "yt-dlp", "--write-auto-sub", "--sub-lang", "en",
        "--sub-format", "vtt", "--skip-download",
        "-o", "subtitle.%(ext)s", video_url
    ]
    try:
        subprocess.run(command, check=True, timeout=120)  # Timeout to prevent hanging
    except subprocess.TimeoutExpired:
        raise Exception("Download timed out. Try another video.")

def extract_text_from_vtt(file_path):
    transcript = []
    for caption in webvtt.read(file_path):
        transcript.append(caption.text)
    return " ".join(transcript)

def summarize_text(text, num_sentences=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    try:
        download_subtitles(video_url)
        transcript = extract_text_from_vtt("subtitle.en.vtt")
        summary = summarize_text(transcript)

        return jsonify({"transcript": transcript, "summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve  # Use a production-ready server
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

import os
import subprocess
import webvtt
from flask import Flask, request, jsonify
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)

# Function to download subtitles
def download_subtitles(video_url):
    command = [
        "yt-dlp", "--write-auto-sub", "--sub-lang", "en",
        "--sub-format", "vtt", "--skip-download",
        "-o", "subtitle.%(ext)s", video_url
    ]
    subprocess.run(command, check=True)

# Function to extract text from VTT file
def extract_text_from_vtt(file_path):
    transcript = []
    for caption in webvtt.read(file_path):
        transcript.append(caption.text)
    return " ".join(transcript)

# Function to summarize text
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
        # Download subtitles
        download_subtitles(video_url)

        # Extract transcript
        transcript = extract_text_from_vtt("subtitle.en.vtt")

        # Summarize transcript
        summary = summarize_text(transcript)

        return jsonify({"transcript": transcript, "summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

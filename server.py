from flask import Flask, request, jsonify
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry["text"] for entry in transcript])
        return text
    except Exception as e:
        return str(e)

@app.route('/transcript', methods=['GET'])
def fetch_transcript():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"success": False, "error": "Missing video_id parameter"}), 400
    
    transcript = get_transcript(video_id)
    return jsonify({"success": True, "transcript": transcript})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

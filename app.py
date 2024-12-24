from flask import Flask, request, jsonify, send_file
import tempfile

try:
    from pytube import YouTube
    import yt_dlp  # For TikTok, Instagram, Facebook, and other platforms
except ImportError:
    raise ImportError("Please install 'pytube' and 'yt_dlp' libraries to proceed.")

app = Flask(__name__)


def download_youtube(link):
    """Download YouTube video."""
    try:
        yt = YouTube(link)
        stream = yt.streams.get_highest_resolution()
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        file_path = stream.download(output_path=temp_file.name)
        return {"status": "success", "file_path": file_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def download_with_ytdlp(link):
    """Download video using yt-dlp."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        ydl_opts = {
            'outtmpl': temp_file.name,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return {"status": "success", "file_path": temp_file.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route('/download', methods=['GET'])
def download_video():
    """Handle video download requests."""
    # Get the URL from the query parameter
    link = request.args.get('url')

    if not link:
        return jsonify({"status": "error", "message": "Link not provided"}), 400

    # Check the platform
    if "youtube.com" in link or "youtu.be" in link:
        result = download_youtube(link)
    elif "tiktok.com" in link or "instagram.com" in link or "facebook.com" in link:
        result = download_with_ytdlp(link)
    else:
        return jsonify({"status": "error", "message": "Unsupported platform"}), 400

    if result["status"] == "success":
        # Serve the file directly
        return send_file(result["file_path"], as_attachment=True)
    else:
        return jsonify(result), 500


if __name__ == '__main__':
    # Use host and port from the environment for Vercel
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

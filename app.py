from flask import Flask, request, jsonify, send_file
import yt_dlp as youtube_dl
import instaloader
import facebook
import re
import io

app = Flask(__name__)

# Helper functions to download content from each platform

def download_youtube_video(url):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'outtmpl': '-',  # Output to stdout (in-memory)
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_data = ydl.prepare_filename(info_dict)
            return video_data
    except Exception as e:
        return {"error": str(e)}

def download_instagram_post(url):
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, url)
        post_data = io.BytesIO()
        loader.download_post(post, target=post_data)
        return post_data
    except Exception as e:
        return {"error": str(e)}

def download_facebook_video(url):
    try:
        # You'll need a Facebook access token
        access_token = 'your_facebook_access_token'
        graph = facebook.GraphAPI(access_token)
        video_id = re.search(r"video.php\?v=(\d+)", url).group(1)
        video = graph.get_object(f"{video_id}?fields=source")
        video_url = video['source']
        # Using yt-dlp to download the video
        ydl_opts = {'quiet': True, 'outtmpl': '-'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_data = ydl.prepare_filename(info_dict)
            return video_data
    except Exception as e:
        return {"error": str(e)}

def download_tiktok_video(url):
    try:
        # Using yt-dlp to download TikTok video
        ydl_opts = {'quiet': True, 'outtmpl': '-'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_data = ydl.prepare_filename(info_dict)
            return video_data
    except Exception as e:
        return {"error": str(e)}

# Flask route to handle video downloads
@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url', '')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Determine the platform based on the URL
    if 'youtube.com' in url or 'youtu.be' in url:
        video_data = download_youtube_video(url)
    elif 'instagram.com' in url:
        video_data = download_instagram_post(url)
    elif 'facebook.com' in url:
        video_data = download_facebook_video(url)
    elif 'tiktok.com' in url:
        video_data = download_tiktok_video(url)
    else:
        return jsonify({"error": "Unsupported platform"}), 400

    if isinstance(video_data, dict) and 'error' in video_data:
        return jsonify(video_data), 400

    return send_file(io.BytesIO(video_data), as_attachment=True, download_name="downloaded_content.mp4")

if __name__ == '__main__':
    app.run(debug=True)

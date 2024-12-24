from flask import Flask, request, jsonify
import yt_dlp as youtube_dl
import instaloader
import facebook
import re
import os

app = Flask(__name__)

# Helper functions to download content from each platform

def download_youtube_video(url):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return {"message": "Video downloaded", "filename": info_dict['title'] + "." + info_dict['ext']}
    except Exception as e:
        return {"error": str(e)}

def download_instagram_post(url):
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, url)
        filename = f"downloads/{post.shortcode}.jpg"
        loader.download_post(post, target=filename)
        return {"message": "Post downloaded", "filename": filename}
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
        ydl_opts = {'outtmpl': 'downloads/facebook_video.%(ext)s'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return {"message": "Facebook video downloaded"}
    except Exception as e:
        return {"error": str(e)}

def download_tiktok_video(url):
    try:
        # Using yt-dlp to download TikTok video
        ydl_opts = {'outtmpl': 'downloads/tiktok_video.%(ext)s'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {"message": "TikTok video downloaded"}
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
        result = download_youtube_video(url)
    elif 'instagram.com' in url:
        result = download_instagram_post(url)
    elif 'facebook.com' in url:
        result = download_facebook_video(url)
    elif 'tiktok.com' in url:
        result = download_tiktok_video(url)
    else:
        return jsonify({"error": "Unsupported platform"}), 400

    return jsonify(result)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)

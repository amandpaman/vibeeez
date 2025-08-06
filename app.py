import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random

st.set_page_config(page_title="YouTube Viewer", page_icon="▶️")
st.title("🎬 Resilient YouTube Viewer")

# User-Agent rotation to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
]

def extract_video_data(html):
    """Extract video data from YouTube HTML"""
    pattern = r'"videoRenderer":\{"videoId":"(.+?)".*?"title":\{"runs":\[\{"text":"(.+?)"\}'
    matches = re.finditer(pattern, html)
    videos = []
    for match in matches:
        video_id = match.group(1)
        title = match.group(2)
        videos.append({
            "title": title,
            "url": f"https://youtu.be/{video_id}",
            "embed_url": f"https://www.youtube.com/embed/{video_id}"
        })
        if len(videos) >= 5:
            break
    return videos

def search_youtube_direct(query):
    """Search YouTube directly with multiple attempts"""
    for attempt in range(3):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9"
            }
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if we got a CAPTCHA page
            if "www.youtube.com/sorry" in response.url:
                st.warning("YouTube is asking for CAPTCHA verification")
                return []
                
            return extract_video_data(response.text)
        except Exception as e:
            if attempt == 2:
                st.error(f"Final attempt failed: {str(e)}")
            continue
    return []

# Main App
search_query = st.text_input("Search YouTube videos", placeholder="Try 'popular music' or 'news'")

if search_query:
    with st.spinner("Connecting to YouTube..."):
        videos = search_youtube_direct(search_query)
    
    if videos:
        st.success(f"Found {len(videos)} videos")
        for video in videos:
            with st.expander(video["title"]):
                try:
                    st.video(video["embed_url"])
                except:
                    st.markdown(f"[Watch on YouTube]({video['url']})")
                st.write("---")
    else:
        st.error("""
        Couldn't fetch results. Possible solutions:
        1. Try simpler/more common search terms
        2. Check your internet connection
        3. Wait a few minutes and try again
        4. Use a VPN if YouTube is blocked
        """)
        st.markdown("As a last resort, you can use the direct URL option below.")

# Direct URL fallback
st.write("---")
st.subheader("Alternative: Enter Direct YouTube URL")
video_url = st.text_input("Paste YouTube URL here", key="direct_url")

if video_url:
    if any(x in video_url for x in ["youtube.com", "youtu.be"]):
        try:
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            st.video(f"https://www.youtube.com/embed/{video_id}")
        except:
            st.video(video_url)  # Fallback
    else:
        st.error("Please enter a valid YouTube URL")

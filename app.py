import streamlit as st
from bs4 import BeautifulSoup
import requests
import urllib.parse

# App Configuration
st.set_page_config(page_title="YouTube Viewer", page_icon="▶️")
st.title("🎬 Alternative YouTube Viewer")

# Helper Functions
def search_youtube(query):
    """Search videos using Invidious"""
    try:
        base_url = "https://vid.puffyan.us"  # Alternative: "https://inv.riverside.rocks"
        search_url = f"{base_url}/search?q={urllib.parse.quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        r = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        results = []
        for item in soup.select(".pure-g .pure-u-1"):
            title = item.select_one("h2")
            link = item.select_one("a[href^='/watch']")
            if title and link:
                results.append({
                    "title": title.text.strip(),
                    "url": f"{base_url}{link['href']}",
                    "embed_url": f"{base_url}/embed{link['href'].split('?')[0]}"
                })
            if len(results) >= 5:
                break
        return results
        
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return []

# Main App
search_query = st.text_input("Search YouTube videos", placeholder="Enter keywords...")

if search_query:
    with st.spinner("Searching through alternative gateway..."):
        videos = search_youtube(search_query)
    
    if videos:
        st.success(f"Found {len(videos)} results")
        for video in videos:
            st.subheader(video["title"])
            
            # Try to embed video
            try:
                st.video(video["embed_url"])
            except:
                st.warning("Embed blocked - Watch directly:")
                st.markdown(f"[▶️ Watch Video]({video['url']})")
            
            st.write("---")
    else:
        st.warning("No videos found. Try different keywords.")

# Direct URL fallback
st.write("---")
st.subheader("Or enter direct YouTube URL")
video_url = st.text_input("Paste YouTube URL here", placeholder="https://youtu.be/...")

if video_url:
    if "youtube.com" in video_url or "youtu.be" in video_url:
        try:
            # Convert to embeddable format
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            
            embed_url = f"https://vid.puffyan.us/embed/{video_id}"
            st.video(embed_url)
        except:
            st.video(video_url)  # Fallback to original URL
    else:
        st.error("Please enter a valid YouTube URL")

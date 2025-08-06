import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random

# App Configuration
st.set_page_config(page_title="YouTube Viewer", page_icon="▶️")
st.title("🎬 Universal YouTube Viewer")

# List of alternative frontends (rotated for reliability)
FRONTENDS = [
    "https://vid.puffyan.us",
    "https://invidious.snopyta.org",
    "https://yewtu.be",
    "https://inv.riverside.rocks"
]

# Helper Functions
def try_search(query, frontend):
    """Try searching using a specific frontend"""
    try:
        search_url = f"{frontend}/search?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(search_url, headers=headers, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        results = []
        
        for item in soup.select(".pure-g .pure-u-1"):
            title = item.select_one("h2")
            link = item.select_one("a[href^='/watch']")
            if title and link:
                results.append({
                    "title": title.text.strip(),
                    "url": f"{frontend}{link['href']}",
                    "embed_url": f"{frontend}/embed{link['href'].split('?')[0]}"
                })
            if len(results) >= 5:
                break
        return results
    except:
        return None

def search_youtube(query):
    """Try multiple frontends until successful"""
    for frontend in random.sample(FRONTENDS, len(FRONTENDS)):
        results = try_search(query, frontend)
        if results is not None:
            return results
    return []

# Main App
search_query = st.text_input("Search YouTube videos", placeholder="Enter keywords...")

if search_query:
    with st.spinner("Searching through alternative gateways..."):
        videos = search_youtube(search_query)
    
    if videos:
        st.success(f"Found {len(videos)} results")
        for video in videos:
            with st.container():
                st.subheader(video["title"])
                
                # Try to embed video
                try:
                    st.video(video["embed_url"])
                except:
                    st.warning("Embed blocked - Watch directly:")
                    st.markdown(f"[▶️ Watch on {video['url'].split('/')[2]}]({video['url']})")
                
                st.write("---")
    else:
        st.error("""
        Couldn't fetch results. This might be because:
        - All alternative gateways are temporarily unavailable
        - Your network is blocking all frontends
        - The search terms are too specific
        
        Try again later or use the direct URL option below.
        """)

# Direct URL fallback
st.write("---")
st.subheader("Alternative: Enter Direct YouTube URL")
video_url = st.text_input("Paste YouTube URL here", placeholder="https://youtu.be/...", key="direct_url")

if video_url:
    if any(x in video_url for x in ["youtube.com", "youtu.be"]):
        try:
            # Convert to embeddable format
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            
            # Try multiple frontends for embedding
            for frontend in FRONTENDS:
                embed_url = f"{frontend}/embed/{video_id}"
                try:
                    st.video(embed_url)
                    break
                except:
                    continue
            else:
                st.video(video_url)  # Final fallback
                
        except Exception as e:
            st.error(f"Couldn't embed video: {str(e)}")
            st.markdown(f"[Open on YouTube]({video_url})")
    else:
        st.error("Please enter a valid YouTube URL (youtube.com or youtu.be)")

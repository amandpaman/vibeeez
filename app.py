import streamlit as st
import feedparser
import urllib.parse
import requests
from bs4 import BeautifulSoup

st.title("🔒 Organization-Friendly YouTube Viewer")
st.markdown("""
<style>
.small-font { font-size:0.9rem !important; }
</style>
""", unsafe_allow_html=True)

# Method 1: YouTube RSS Feed Search (works in many restricted networks)
def search_rss(query):
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?search_query={urllib.parse.quote(query)}"
        feed = feedparser.parse(url)
        return [{
            'title': entry.title,
            'url': entry.link,
            'embed_url': f"https://www.youtube.com/embed/{entry.yt_videoid}"
        } for entry in feed.entries[:5]]
    except:
        return None

# Method 2: Public JSON endpoint scraping
def search_public_json(query):
    try:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        for script in scripts:
            if 'var ytInitialData =' in script.text:
                data = json.loads(script.text.split('var ytInitialData =')[1].split(';')[0])
                # Parse the complex JSON structure here
                # This would need more detailed implementation
                return []  # Placeholder
        return None
    except:
        return None

# Method 3: Educational API fallback
def search_educational(query):
    try:
        # Uses the Internet Archive's YouTube metadata
        url = f"https://archive.org/wayback/available?url=youtube.com/results?search_query={urllib.parse.quote(query)}"
        response = requests.get(url, timeout=10).json()
        if 'archived_snapshots' in response:
            snapshot_url = response['archived_snapshots']['closest']['url']
            # Would need to parse the archived page
            return []  # Placeholder
        return None
    except:
        return None

# Main search function with multiple fallbacks
def search_youtube(query):
    methods = [
        ("RSS Feed", search_rss),
        ("Public JSON", search_public_json),
        ("Educational Archive", search_educational)
    ]
    
    for method_name, method_func in methods:
        with st.spinner(f"Trying {method_name}..."):
            results = method_func(query)
            if results:
                return results, method_name
    return None, None

# Search interface
search_query = st.text_input("Search for videos")
if search_query:
    results, method = search_youtube(search_query)
    
    if results:
        st.success(f"Found {len(results)} results via {method}")
        for video in results:
            with st.expander(video['title']):
                try:
                    st.video(video['embed_url'])
                except:
                    st.markdown(f"[Watch on YouTube]({video['url']})")
                st.markdown(f'<p class="small-font">Method: {method}</p>', unsafe_allow_html=True)
    else:
        st.error("""
        Couldn't fetch results through any method. Try:
        1. Different search terms
        2. The direct URL option below
        3. Checking with your IT department
        """)

# Direct URL fallback
st.write("---")
st.subheader("Alternative: Direct URL")
video_url = st.text_input("Paste any YouTube URL", key="direct_url")
if video_url:
    if any(x in video_url for x in ["youtube.com", "youtu.be"]):
        try:
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            
            # Try multiple embed methods
            embed_methods = [
                ("Standard", f"https://www.youtube.com/embed/{video_id}"),
                ("No-Cookie", f"https://www.youtube-nocookie.com/embed/{video_id}"),
                ("Alternative", f"https://yewtu.be/embed/{video_id}")
            ]
            
            for name, url in embed_methods:
                try:
                    st.video(url)
                    st.caption(f"Embed method: {name}")
                    break
                except:
                    continue
            else:
                st.markdown(f"[Watch Directly]({video_url})")
        except:
            st.error("Couldn't process this URL")
    else:
        st.error("Please enter a valid YouTube URL")

st.markdown("""
---
### Troubleshooting Guide:
1. **If nothing works** - Try simpler search terms
2. **For strict networks** - Use during off-peak hours
3. **Last resort** - Download videos at home and use offline
""")

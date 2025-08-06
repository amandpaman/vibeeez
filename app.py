import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

# Configuration
SEARCH_PROVIDERS = [
    {
        "name": "Invidious (Puffyan)",
        "url": "https://vid.puffyan.us/search?q={query}",
        "parser": "invidious"
    },
    {
        "name": "YouTube Proxy",
        "url": "https://ytproxy.vercel.app/search?q={query}",
        "parser": "json"
    }
]

# Helper functions
def search_invidious(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for item in soup.select(".pure-g .pure-u-1"):
        title = item.select_one("h2")
        link = item.select_one("a[href^='/watch']")
        if title and link:
            results.append({
                "title": title.text.strip(),
                "url": f"https://vid.puffyan.us{link['href']}",
                "embed_url": f"https://vid.puffyan.us/embed{link['href'].split('?')[0]}"
            })
        if len(results) >= 5:
            break
    return results

def search_json(response):
    data = response.json()
    return [{
        "title": item['title'],
        "url": item['url'],
        "embed_url": item['embed_url']
    } for item in data[:5]]

# Main app
st.title("🎬 Organization-Friendly YouTube Viewer")

# Search section
search_query = st.text_input("Search videos")

if search_query:
    results = None
    for provider in SEARCH_PROVIDERS:
        try:
            st.info(f"Trying {provider['name']}...")
            url = provider["url"].format(query=urllib.parse.quote(search_query))
            response = requests.get(url, timeout=10)
            
            if provider["parser"] == "invidious":
                results = search_invidious(response.text)
            elif provider["parser"] == "json":
                results = search_json(response)
                
            if results:
                break
                
        except Exception as e:
            st.warning(f"Failed with {provider['name']}: {str(e)}")
            continue
    
    if results:
        st.success("Found results!")
        for video in results:
            with st.expander(video["title"]):
                try:
                    st.video(video["embed_url"])
                except:
                    st.markdown(f"[Watch on {provider['name']}]({video['url']})")
    else:
        st.error("""
        Couldn't fetch results. This might be because:
        1. All alternative providers are blocked
        2. Your organization has strict network filters
        3. The search terms are too specific
        
        Try using the direct URL option below with a VPN.
        """)

# Direct URL section
st.write("---")
st.subheader("Alternative: Use Direct URL")
video_url = st.text_input("Paste any YouTube URL")

if video_url:
    if any(x in video_url for x in ["youtube.com", "youtu.be"]):
        try:
            # Extract video ID
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            
            # Try multiple embed methods
            embed_urls = [
                f"https://vid.puffyan.us/embed/{video_id}",
                f"https://ytproxy.vercel.app/embed/{video_id}",
                f"https://www.youtube.com/embed/{video_id}"
            ]
            
            for url in embed_urls:
                try:
                    st.video(url)
                    break
                except:
                    continue
            else:
                st.markdown(f"[Watch on YouTube]({video_url})")
        except:
            st.error("Couldn't process this URL")
    else:
        st.error("Please enter a valid YouTube URL")

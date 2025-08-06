import streamlit as st
import requests
from bs4 import BeautifulSoup

def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    videos = []
    
    for vid in soup.find_all('a', {'href': lambda x: x and x.startswith('/watch?v=')}):
        video_id = vid['href'][9:20]  # Extract 11-character video ID
        if video_id and len(video_id) == 11:
            videos.append({
                'link': f"https://youtube.com/watch?v={video_id}",
                'title': vid.get('title', 'No title')
            })
            if len(videos) >= 5: break
    return videos

st.title("🎬 YouTube Search")

search_query = st.text_input("Search YouTube videos")

if search_query:
    videos = search_youtube(search_query)
    for video in videos:
        st.write(f"### {video['title']}")
        st.video(video['link'])
        st.write("---")

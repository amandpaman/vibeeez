import streamlit as st
import subprocess
import tempfile
import base64
import os
import json
import time
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="YouTube Stream Player",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF0000;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .stream-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .video-player {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_yt_dlp():
    """Check if yt-dlp is available"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if len(url) == 11 and url.replace('-', '').replace('_', '').isalnum():
        return url
    
    return None

def get_video_info(url):
    """Get video information using yt-dlp"""
    try:
        cmd = ['yt-dlp', '--dump-json', '--no-download', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return {
                'title': info.get('title', 'Unknown Title'),
                'uploader': info.get('uploader', 'Unknown Channel'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:300] + '...' if info.get('description') else '',
                'upload_date': info.get('upload_date', ''),
                'thumbnail': info.get('thumbnail', ''),
                'webpage_url': info.get('webpage_url', url)
            }
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
    
    return None

def get_video_stream_url(url, quality='720p'):
    """Get direct video stream URL"""
    try:
        # Get the best format URL for streaming
        format_selector = f"best[height<={quality[:-1]}][ext=mp4]/best[ext=mp4]/best"
        
        cmd = [
            'yt-dlp', 
            '-f', format_selector,
            '--get-url',
            '--no-playlist',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
            
    except Exception as e:
        st.error(f"Error getting stream URL: {str(e)}")
    
    return None

def download_small_video(url, max_size_mb=50):
    """Download small video to memory for preview"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            cmd = [
                'yt-dlp',
                '-f', f'best[filesize<{max_size_mb}M][ext=mp4]/worst[ext=mp4]',
                '-o', temp_file.name,
                '--no-playlist',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(temp_file.name):
                # Read file to memory
                with open(temp_file.name, 'rb') as f:
                    video_data = f.read()
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return video_data
                
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
    
    return None

def create_video_player(video_data):
    """Create HTML5 video player with base64 encoded video"""
    if video_data:
        video_base64 = base64.b64encode(video_data).decode()
        
        video_html = f"""
        <div class="video-player">
            <video width="100%" height="400" controls preload="metadata">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        """
        
        return video_html
    
    return None

def main():
    st.markdown('<h1 class="main-header">🎬 YouTube Stream Player</h1>', unsafe_allow_html=True)
    
    # Check if yt-dlp is available
    if not check_yt_dlp():
        st.error("⚠️ yt-dlp is not available in this deployment environment.")
        st.markdown("""
        ### Alternative Solutions:
        1. **Use YouTube Embed (if not blocked):** Direct iframe embedding
        2. **Download locally:** Use the local version of this app
        3. **VPN/Proxy:** Use network tools to access YouTube directly
        """)
        
        # Fallback to embed mode
        st.subheader("🔗 YouTube Embed Mode")
        embed_url = st.text_input("Enter YouTube URL for embed:")
        
        if embed_url:
            video_id = extract_video_id(embed_url)
            if video_id:
                embed_html = f"""
                <iframe width="100%" height="400" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" allowfullscreen>
                </iframe>
                """
                st.markdown(embed_html, unsafe_allow_html=True)
                st.warning("This will only work if YouTube is not blocked in your network.")
        
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Settings")
        
        # Quality selection
        quality = st.selectbox(
            "Stream Quality",
            ["1080p", "720p", "480p", "360p", "240p"],
            index=1
        )
        
        # Processing options
        download_mode = st.radio(
            "Processing Mode",
            ["Stream URL", "Download Small Video", "Audio Only"],
            help="Stream URL: Get direct link, Download: Process small videos, Audio: Extract audio"
        )
        
        # Size limit for downloads
        if download_mode == "Download Small Video":
            max_size = st.slider("Max Video Size (MB)", 10, 100, 50)
        
        st.markdown("---")
        
        # Information
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        **Stream URL Mode:**
        - Gets direct video link
        - Best for larger videos
        - Requires external player
        
        **Download Mode:**  
        - Downloads small videos
        - Plays in browser
        - Limited by size
        
        **Audio Mode:**
        - Extracts audio only
        - Smaller file size
        - Good for music
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input section
        st.markdown('<div class="stream-section">', unsafe_allow_html=True)
        st.subheader("🔗 Enter YouTube URL")
        
        video_url = st.text_input(
            "YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            help="Paste any YouTube video URL"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            get_info_btn = st.button("📋 Get Video Info")
        
        with col_btn2:
            process_btn = st.button("🎬 Process Video")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process video info
        if get_info_btn and video_url:
            with st.spinner("Getting video information..."):
                info = get_video_info(video_url)
                if info:
                    st.session_state.video_info = info
                    st.success("✅ Video information retrieved!")
                else:
                    st.error("❌ Failed to get video information")
        
        # Display video info
        if 'video_info' in st.session_state:
            info = st.session_state.video_info
            
            st.subheader("📺 Video Information")
            
            # Show thumbnail if available
            if info.get('thumbnail'):
                st.image(info['thumbnail'], width=300)
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Title:** {info['title']}")
                st.write(f"**Channel:** {info['uploader']}")
                if info['duration']:
                    minutes = info['duration'] // 60
                    seconds = info['duration'] % 60
                    st.write(f"**Duration:** {minutes}:{seconds:02d}")
            
            with col_info2:
                if info['view_count']:
                    st.write(f"**Views:** {info['view_count']:,}")
                st.write(f"**Upload Date:** {info['upload_date']}")
            
            with st.expander("Description"):
                st.write(info['description'])
        
        # Process video
        if process_btn and video_url:
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("❌ Invalid YouTube URL")
                return
            
            if download_mode == "Stream URL":
                with st.spinner("Getting stream URL..."):
                    stream_url = get_video_stream_url(video_url, quality)
                    if stream_url:
                        st.success("✅ Stream URL obtained!")
                        st.code(stream_url)
                        st.markdown(f"[🔗 Open Stream URL]({stream_url})")
                        
                        # Try to embed if possible
                        try:
                            st.video(stream_url)
                        except:
                            st.warning("Could not embed stream. Use the URL above in your video player.")
                    else:
                        st.error("❌ Failed to get stream URL")
            
            elif download_mode == "Download Small Video":
                with st.spinner(f"Downloading video (max {max_size}MB)..."):
                    video_data = download_small_video(video_url, max_size)
                    if video_data:
                        st.success(f"✅ Video downloaded! ({len(video_data)/1024/1024:.1f} MB)")
                        
                        # Create and display video player
                        video_html = create_video_player(video_data)
                        if video_html:
                            st.markdown(video_html, unsafe_allow_html=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Video File",
                            data=video_data,
                            file_name=f"video_{video_id}.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error("❌ Failed to download video. Try a smaller video or different quality.")
            
            elif download_mode == "Audio Only":
                with st.spinner("Extracting audio..."):
                    # This would extract audio - simplified for demo
                    st.info("🎵 Audio extraction would be implemented here")
                    st.warning("Audio mode requires additional implementation for cloud deployment")
    
    with col2:
        # Cloud deployment warning
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.subheader("☁️ Cloud Deployment Notice")
        st.markdown("""
        **This app is deployed on the cloud:**
        - ✅ Can get video information
        - ✅ Can extract stream URLs  
        - ⚠️ Limited video downloading (size restrictions)
        - ⚠️ No persistent storage
        - 🔗 Best for getting stream links
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Usage tips
        st.subheader("💡 Usage Tips")
        st.markdown("""
        **For blocked YouTube access:**
        1. Use "Stream URL" mode
        2. Copy the generated URL
        3. Open in VLC or other player
        4. Or use proxy/VPN with the URL
        
        **For small videos:**
        1. Use "Download Small Video"
        2. Play directly in browser
        3. Download for offline use
        """)
        
        # System status
        st.subheader("🔧 System Status")
        st.write(f"**yt-dlp:** {'✅ Available' if check_yt_dlp() else '❌ Not available'}")
        st.write(f"**Environment:** Cloud Deployment")
        st.write(f"**Storage:** Temporary")
        
        # Quick links
        st.subheader("🔗 Quick Test Videos")
        test_videos = {
            "Rick Astley - Never Gonna Give You Up": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "Big Buck Bunny (Short)": "https://www.youtube.com/watch?v=YE7VzlLtp-4",
            "Test Video (Very Short)": "https://www.youtube.com/watch?v=BaW_jenozKc"
        }
        
        for title, url in test_videos.items():
            if st.button(title, key=f"test_{url.split('=')[-1]}"):
                st.session_state.test_url = url
                st.rerun()

if __name__ == "__main__":
    main()

import streamlit as st
import yt_dlp
import os
import uuid
import time
import random

def download_video(url, output_path):
    # Add random delay to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'force_ipv4': True,
        'socket_timeout': 30,
        'http_chunk_size': 10485760,
        'sleep_interval': 2,
        'max_sleep_interval': 5,
        # Enhanced headers to mimic real browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        },
        # Instagram specific settings
        'extractor_args': {
            'instagram': {
                'extract_reels': True,
                'skip_auth': True,
            }
        },
        # Retry settings
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to check if video is available
            info_dict = ydl.extract_info(url, download=False)
            
            # Check if it's a reel and has formats available
            if 'formats' not in info_dict or not info_dict['formats']:
                raise Exception("No video formats available for this reel")
            
            # Now download the video
            ydl.download([url])
        return True
        
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if "private" in error_msg:
            raise Exception("This reel is private and cannot be downloaded")
        elif "rate limit" in error_msg or "too many requests" in error_msg:
            raise Exception("Rate limit reached. Please try again in a few minutes.")
        elif "login required" in error_msg:
            raise Exception("Login required. This reel might be age-restricted or require Instagram login.")
        elif "unavailable" in error_msg or "not available" in error_msg:
            raise Exception("The requested content is not available or has been removed.")
        else:
            raise Exception(f"Download failed: {str(e)}")
    
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

def main():
    # Page configuration
    st.set_page_config(
        page_title="Instagram Reel Downloader",
        page_icon="📱",
        layout="centered"
    )
    
    # Custom CSS for clean styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        color: #262730;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #FF6B6B;
        color: white;
    }
    .stButton button:disabled {
        background-color: #CCCCCC;
        color: #666666;
    }
    .stTextInput input {
        border-radius: 8px;
        padding: 0.75rem;
        border: 2px solid #E0E0E0;
        font-size: 1rem;
    }
    .stTextInput input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2);
    }
    .success-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #F0FFF4;
        border: 1px solid #9AE6B4;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #FED7D7;
        border: 1px solid #FC8181;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #E6F3FF;
        border: 1px solid #90CDF4;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="main-header">📱 Instagram Reel Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
    # URL input section
    url = st.text_input(
        "Enter Instagram Reel URL",
        placeholder="https://www.instagram.com/reel/ABC123...",
        key="url_input",
        help="Paste the full URL of a public Instagram reel"
    )
    
    # Information box
    st.markdown("""
    <div class="info-box">
    <strong>💡 Important Notes:</strong>
    <ul>
    <li>Only works with <strong>public</strong> Instagram reels</li>
    <li>Private or age-restricted reels cannot be downloaded</li>
    <li>If download fails, wait a few minutes and try again</li>
    <li>Make sure the URL contains "instagram.com/reel/"</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    download_clicked = st.button(
        "⬇️ Download Reel", 
        key="download", 
        type="primary", 
        use_container_width=True,
        disabled=not url
    )
    
    # Handle download process
    if download_clicked and url:
        # Validate URL format
        if not ("instagram.com" in url and "/reel/" in url):
            st.markdown("""
            <div class="error-box">
            <strong>❌ Invalid URL Format</strong><br>
            Please make sure the URL is a valid Instagram Reel link containing "instagram.com/reel/"
            </div>
            """, unsafe_allow_html=True)
        else:
            unique_id = str(uuid.uuid4())
            output_path = f"downloaded_video_{unique_id}.mp4"
            
            try:
                with st.spinner("🔄 Downloading your reel... This may take 10-30 seconds."):
                    success = download_video(url, output_path)
                
                if success:
                    st.markdown("""
                    <div class="success-box">
                    <strong>✅ Download Completed Successfully!</strong><br>
                    Your Instagram reel has been downloaded and is ready to save.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display download button for the file
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    
                    # Get file size
                    file_size = len(video_bytes) / (1024 * 1024)  # Convert to MB
                    
                    st.download_button(
                        label=f"💾 Save MP4 File ({file_size:.1f} MB)",
                        data=video_bytes,
                        file_name=f"instagram_reel_{unique_id[:8]}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key="save_file"
                    )
                    
                    # Clean up the temporary file
                    try:
                        os.remove(output_path)
                    except:
                        pass
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                <strong>❌ Download Failed</strong><br>
                {str(e)}
                </div>
                """, unsafe_allow_html=True)
                
                # Additional troubleshooting tips
                st.markdown("""
                <div class="info-box">
                <strong>🔧 Troubleshooting Tips:</strong>
                <ul>
                <li>Ensure the reel is <strong>public</strong> (not private)</li>
                <li>Try copying the URL directly from the Instagram app</li>
                <li>Wait 2-3 minutes and try again (rate limiting)</li>
                <li>Check if the reel is still available on Instagram</li>
                <li>Try a different Instagram reel URL</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem; line-height: 1.4;'>"
        "This tool is for downloading publicly available Instagram reels only.<br>"
        "Please respect content creators' rights and download for personal use only."
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
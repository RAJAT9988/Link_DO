import streamlit as st
import yt_dlp
import os
import uuid
import time
import random

def download_video(url, output_path):
    # Add random delay to avoid detection
    time.sleep(random.uniform(2, 5))
    
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        # Add headers to mimic real browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Instagram specific settings
        'extractor_args': {
            'instagram': {
                'extract_reels': True,
            }
        },
        # Rate limiting prevention
        'sleep_interval': 2,
        'max_sleep_interval': 5,
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
            raise Exception("Instagram rate limit reached. Please wait 1-2 hours and try again.")
        elif "private" in str(e).lower():
            raise Exception("This reel is private or requires login.")
        elif "unavailable" in str(e).lower():
            raise Exception("Reel is not available or has been removed.")
        else:
            raise e

def main():
    # Page configuration
    st.set_page_config(
        page_title="Instagram Reel Downloader",
        page_icon="♟",
        layout="centered"
    )
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E1306C;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .download-btn {
        background-color: #E1306C;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-size: 1.1rem;
        cursor: pointer;
        width: 100%;
    }
    .download-btn:hover {
        background-color: #C13584;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .rate-limit-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="main-header"> Instagram Reel Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
    # Rate limit warning
    st.markdown("""
    <div class="info-box">
    <strong>⚠️ Important:</strong> Due to Instagram restrictions, there's a daily download limit. 
    If you get rate limit errors, please try again after some time.
    </div>
    """, unsafe_allow_html=True)
    
    # URL input section
    st.markdown("### Enter Instagram Reel URL")
    
    url = st.text_input(
        "URL",
        placeholder="Paste Instagram Reel link here...",
        label_visibility="collapsed"
    )
    
    # Download button section
    st.markdown("---")
    download_clicked = st.button(
        "⬇️ Download Reel", 
        key="download", 
        type="primary", 
        use_container_width=True,
        disabled=not url
    )
    
    # Handle download process
    if download_clicked and url:
        if not ("instagram.com" in url and "/reel/" in url):
            st.error("Please enter a valid Instagram Reel URL")
        else:
            unique_id = str(uuid.uuid4())
            output_path = f"downloaded_video_{unique_id}.mp4"
            
            try:
                with st.spinner("🔄 Downloading your reel... This may take a few moments."):
                    success = download_video(url, output_path)
                
                if success:
                    st.success("✅ Download completed successfully!")
                    
                    # Display download button for the file
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    
                    st.download_button(
                        label="💾 Save MP4 File",
                        data=video_bytes,
                        file_name=f"instagram_reel_{unique_id}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
                    # Clean up the temporary file
                    try:
                        os.remove(output_path)
                    except:
                        pass
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ {error_msg}")
                
                if "rate limit" in error_msg.lower():
                    st.markdown("""
                    <div class="rate-limit-msg">
                    <strong>📊 Rate Limit Reached</strong><br>
                    Instagram has temporarily blocked downloads from this server. <br>
                    <strong>Solution:</strong> Please try again after 1-2 hours.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💡 Tips: Make sure the URL is correct and the reel is publicly accessible")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Note: Only works with public Instagram Reels • Download for personal use only<br>"
        "Daily download limits may apply due to Instagram restrictions"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
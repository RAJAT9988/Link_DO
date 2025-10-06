import streamlit as st
import yt_dlp
import os
import uuid
import time
import random

def download_video(url, output_path):
    # Add random delay to avoid detection
    time.sleep(random.uniform(3, 7))
    
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        
        # Instagram specific configuration
        'extractor_args': {
            'instagram': {
                'extract_reels': True,
                'cookie': 'yes',  # Enable cookie usage
            }
        },
        
        # Browser emulation
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        },
        
        # Rate limiting prevention
        'sleep_interval': 3,
        'max_sleep_interval': 8,
        'retries': 2,
        'fragment_retries': 2,
        'skip_unavailable_fragments': True,
        'ignoreerrors': False,
        
        # Alternative approach - try different extractors
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
        
    except Exception as e:
        error_str = str(e)
        if "rate-limit" in error_str.lower() or "rate limit" in error_str.lower():
            raise Exception("Instagram has temporarily blocked our server. Please try again in 2-3 hours.")
        elif "login required" in error_str.lower() or "cookies" in error_str.lower():
            raise Exception("This reel requires Instagram login. Try a different public reel or use Instagram's official app.")
        elif "not available" in error_str.lower() or "unavailable" in error_str.lower():
            raise Exception("This reel is not available or has been removed from Instagram.")
        elif "private" in error_str.lower():
            raise Exception("This is a private reel and cannot be downloaded.")
        else:
            raise Exception(f"Download failed: {error_str}")

def main():
    # Page configuration
    st.set_page_config(
        page_title="Instagram Reel Downloader",
        page_icon="📱",
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
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .warning-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        color: #856404;
        margin-bottom: 1.5rem;
    }
    .info-box {
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stButton button {
        background-color: #E1306C;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #C13584;
        color: white;
    }
    .stButton button:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    .stTextInput input {
        border-radius: 8px;
        padding: 0.75rem;
        border: 2px solid #e0e0e0;
        font-size: 1rem;
    }
    .stTextInput input:focus {
        border-color: #E1306C;
        box-shadow: 0 0 0 2px rgba(225, 48, 108, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="main-header">📱 Instagram Reel Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
    # Important warning box
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ Important Notice</strong><br>
    Due to recent Instagram restrictions, some reels may not be downloadable.<br>
    <strong>Works best with:</strong> Public reels from popular accounts
    </div>
    """, unsafe_allow_html=True)
    
    # Tips box
    st.markdown("""
    <div class="info-box">
    <strong>💡 Tips for Better Success:</strong>
    <ul>
    <li>Use reels from public accounts with many followers</li>
    <li>Try reels that are recently posted (not too old)</li>
    <li>If one reel fails, try a different one</li>
    <li>Wait a few hours if you get rate limit errors</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # URL input section
    st.markdown("### Enter Instagram Reel URL")
    
    url = st.text_input(
        "URL",
        placeholder="https://www.instagram.com/reel/ABC123...",
        label_visibility="collapsed",
        key="url_input"
    )
    
    # Download button section
    download_clicked = st.button(
        "⬇️ Download Reel", 
        key="download", 
        type="primary", 
        use_container_width=True,
        disabled=not url
    )
    
    # Handle download process
    if download_clicked and url:
        # Validate URL
        if not ("instagram.com" in url and "/reel/" in url):
            st.error("❌ Please enter a valid Instagram Reel URL")
            st.info("The URL should contain 'instagram.com/reel/'")
        else:
            unique_id = str(uuid.uuid4())
            output_path = f"downloaded_video_{unique_id}.mp4"
            
            try:
                with st.spinner("🔄 Attempting to download... This may take 10-30 seconds."):
                    success = download_video(url, output_path)
                
                if success:
                    st.success("✅ Download completed successfully!")
                    
                    # Display download button for the file
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    
                    # Show file size
                    file_size_mb = len(video_bytes) / (1024 * 1024)
                    
                    st.download_button(
                        label=f"💾 Save MP4 File ({file_size_mb:.1f} MB)",
                        data=video_bytes,
                        file_name=f"instagram_reel_{unique_id[:8]}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key="save_file"
                    )
                    
                    # Clean up temporary file
                    try:
                        os.remove(output_path)
                    except:
                        pass
                    
            except Exception as e:
                error_message = str(e)
                st.error(f"❌ {error_message}")
                
                # Specific troubleshooting based on error type
                if "login required" in error_message.lower():
                    st.markdown("""
                    <div class="info-box">
                    <strong>🔒 Authentication Required</strong><br>
                    This reel requires Instagram login to view. This usually happens with:<br>
                    • Age-restricted content<br>
                    • Content from private accounts<br>
                    • Content in restricted regions<br><br>
                    <strong>Solution:</strong> Try a different public reel from a popular creator.
                    </div>
                    """, unsafe_allow_html=True)
                
                elif "rate limit" in error_message.lower():
                    st.markdown("""
                    <div class="warning-box">
                    <strong>⏰ Rate Limit Reached</strong><br>
                    Instagram has temporarily blocked downloads from our server.<br><br>
                    <strong>Please try:</strong><br>
                    • Waiting 2-3 hours<br>
                    • Using the app during off-peak hours (early morning)<br>
                    • Trying a different reel later
                    </div>
                    """, unsafe_allow_html=True)
                
                else:
                    st.markdown("""
                    <div class="info-box">
                    <strong>🔄 Alternative Solutions:</strong><br>
                    1. Try a different Instagram reel URL<br>
                    2. Make sure the reel is from a public account<br>
                    3. Check if the reel is still available on Instagram<br>
                    4. Wait a few minutes and try again<br>
                    5. Try using Instagram's official download feature (if available)
                    </div>
                    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem; line-height: 1.5;'>"
        "This tool works with publicly available Instagram reels only.<br>"
        "Some restrictions apply due to Instagram's platform policies.<br>"
        "Download for personal use only and respect content creators' rights."
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
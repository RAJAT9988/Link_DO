# import streamlit as st
# import yt_dlp
# import os
# import uuid
# def download_video(url, output_path):
#     ydl_opts = {
#         'format': 'mp4',
#         'outtmpl': output_path,
#         'quiet': True,
#         'no_warnings': True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])

# def main():
#     # Page configuration
#     st.set_page_config(
#         page_title="Instagram Reel Downloader",
#         page_icon="📱",
#         layout="centered"
#     )
    
#     # Custom CSS for professional styling
#     st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #E1306C;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .sub-header {
#         font-size: 1.2rem;
#         color: #555;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .download-btn {
#         background-color: #E1306C;
#         color: white;
#         border: none;
#         padding: 0.5rem 2rem;
#         border-radius: 5px;
#         font-size: 1.1rem;
#         cursor: pointer;
#         width: 100%;
#     }
#     .download-btn:hover {
#         background-color: #C13584;
#     }
#     .success-msg {
#         padding: 1rem;
#         border-radius: 5px;
#         background-color: #d4edda;
#         color: #155724;
#         border: 1px solid #c3e6cb;
#     }
#     .error-msg {
#         padding: 1rem;
#         border-radius: 5px;
#         background-color: #f8d7da;
#         color: #721c24;
#         border: 1px solid #f5c6cb;
#     }
#     .input-container {
#         display: flex;
#         align-items: center;
#         margin-bottom: 1.5rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # Header section
#     st.markdown('<div class="main-header">📱 Instagram Reel Downloader</div>', unsafe_allow_html=True)
#     st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
#     # URL input section without paste button
#     st.markdown("### Enter Instagram Reel URL")
    
#     url = st.text_input(
#         "URL",
#         placeholder="Paste Instagram Reel link here...",
#         label_visibility="collapsed"
#     )
    
#     # Download button section
#     st.markdown("---")
#     download_clicked = st.button(
#         "⬇️ Download Reel", 
#         key="download", 
#         type="primary", 
#         use_container_width=True,
#         disabled=not url
#     )
    
#     # Handle download process
#     if download_clicked and url:
#         if not ("instagram.com" in url and "/reel/" in url):
#             st.error("Please enter a valid Instagram Reel URL")
#         else:
#             unique_id = str(uuid.uuid4())
#             output_path = f"downloaded_video_{unique_id}.mp4"
            
#             try:
#                 with st.spinner("🔄 Downloading your reel... This may take a few moments."):
#                     download_video(url, output_path)
                
#                 st.success("✅ Download completed successfully!")
                
#                 # Display download button for the file
#                 with open(output_path, "rb") as f:
#                     video_bytes = f.read()
                
#                 st.download_button(
#                     label="💾 Save MP4 File",
#                     data=video_bytes,
#                     file_name=f"instagram_reel_{unique_id}.mp4",
#                     mime="video/mp4",
#                     use_container_width=True
#                 )
                
#                 # Clean up the temporary file
#                 try:
#                     os.remove(output_path)
#                 except:
#                     pass
                    
#             except Exception as e:
#                 st.error(f"❌ Error downloading video: {str(e)}")
#                 st.info("💡 Tips: Make sure the URL is correct and the reel is publicly accessible")

#     # Footer
#     st.markdown("---")
#     st.markdown(
#         "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
#         "Note: Only works with public Instagram Reels • Download for personal use only"
#         "</div>", 
#         unsafe_allow_html=True
#     )

# if __name__ == "__main__":
#     main()


import streamlit as st
import yt_dlp
import os
import uuid
import time
from datetime import datetime, timedelta
import requests
import json

# Initialize session state for download tracking
if 'download_count' not in st.session_state:
    st.session_state.download_count = 0
if 'last_reset_time' not in st.session_state:
    st.session_state.last_reset_time = datetime.now()
if 'cooldown_until' not in st.session_state:
    st.session_state.cooldown_until = None
if 'user_agent' not in st.session_state:
    st.session_state.user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"

def get_random_user_agent():
    """Return a random mobile user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ]
    import random
    return random.choice(user_agents)

def download_video(url, output_path, use_cookies=False):
    """Download video with multiple fallback methods"""
    
    # Base options
    ydl_opts = {
        'format': 'best[height<=720]',  # Limit to 720p to reduce detection
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        'sleep_interval': 2,  # Add delay between requests
        'max_sleep_interval': 5,
        'user_agent': get_random_user_agent(),
        'extracter_retries': 3,
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
        'ignoreerrors': True,
    }
    
    # Method 1: Try with browser cookies first
    if use_cookies:
        try:
            # Try different browsers
            for browser in ['chrome', 'firefox', 'edge', 'safari']:
                try:
                    ydl_opts['cookiesfrombrowser'] = (browser,)
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    return True
                except:
                    continue
        except:
            pass
    
    # Method 2: Try with custom headers (mobile emulation)
    ydl_opts.update({
        'http_headers': {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except:
        pass
    
    # Method 3: Try without any special options as last resort
    try:
        basic_opts = {
            'format': 'best[height<=720]',
            'outtmpl': output_path,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(basic_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        raise e

def can_download():
    """Check if user can download based on limits"""
    current_time = datetime.now()
    
    # Reset counter every 2 hours
    if current_time - st.session_state.last_reset_time > timedelta(hours=2):
        st.session_state.download_count = 0
        st.session_state.last_reset_time = current_time
        st.session_state.cooldown_until = None
    
    # Check if in cooldown period
    if st.session_state.cooldown_until and current_time < st.session_state.cooldown_until:
        return False, "cooldown"
    
    # Check download limit (3 downloads per 2 hours)
    if st.session_state.download_count >= 3:
        # Set cooldown for 2 hours
        st.session_state.cooldown_until = current_time + timedelta(hours=2)
        return False, "limit_reached"
    
    return True, "ok"

def update_download_count():
    """Update download counter"""
    st.session_state.download_count += 1

def get_cooldown_time_remaining():
    """Get remaining cooldown time in readable format"""
    if st.session_state.cooldown_until:
        remaining = st.session_state.cooldown_until - datetime.now()
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
    return "0h 0m"

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
    .info-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    .limit-info {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .cookie-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #E1306C;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="main-header">📱 Instagram Reel Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
    # Download limit info
    st.markdown(f"""
    <div class="limit-info">
    📊 Downloads used: {st.session_state.download_count}/3 (resets in 2 hours) 
    {f"⏰ Cooldown: {get_cooldown_time_remaining()} remaining" if st.session_state.cooldown_until else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Cookie configuration section
    st.markdown("### 🔧 Authentication Setup (Required)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_cookies = st.checkbox("Use Browser Cookies", value=True, 
                                 help="Automatically use cookies from your browser")
        
    with col2:
        browser_type = st.selectbox(
            "Select Browser",
            ["chrome", "firefox", "edge", "safari"],
            help="Select the browser where you're logged into Instagram"
        )
    
    # URL input section
    st.markdown("### Enter Instagram Reel URL")
    
    url = st.text_input(
        "URL",
        placeholder="Paste Instagram Reel link here...",
        label_visibility="collapsed"
    )
    
    # Download button section
    st.markdown("---")
    
    # Check download eligibility
    can_download_result, reason = can_download()
    
    if reason == "cooldown":
        st.error(f"⏰ Rate limit reached. Please try again in {get_cooldown_time_remaining()}.")
        download_disabled = True
    elif reason == "limit_reached":
        st.error("🚫 Download limit reached (3 downloads per 2 hours). Please wait 2 hours.")
        download_disabled = True
    else:
        download_disabled = not url
    
    download_clicked = st.button(
        "⬇️ Download Reel", 
        key="download", 
        type="primary", 
        use_container_width=True,
        disabled=download_disabled
    )
    
    # Handle download process
    if download_clicked and url and can_download_result:
        if not ("instagram.com" in url):
            st.error("❌ Please enter a valid Instagram URL")
        else:
            unique_id = str(uuid.uuid4())
            output_path = f"downloaded_video_{unique_id}.mp4"
            
            try:
                with st.spinner("🔄 Downloading your reel... This may take a few moments."):
                    # Set cookies option based on user selection
                    download_success = download_video(url, output_path, use_cookies=use_cookies)
                
                if download_success and os.path.exists(output_path):
                    # Update download count
                    update_download_count()
                    
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
                    
                    # Show remaining downloads
                    remaining_downloads = 3 - st.session_state.download_count
                    if remaining_downloads > 0:
                        st.info(f"📊 You have {remaining_downloads} download(s) remaining in this 2-hour period.")
                    else:
                        st.warning("⚠️ You've reached your download limit for the next 2 hours.")
                    
                    # Clean up the temporary file
                    try:
                        os.remove(output_path)
                    except:
                        pass
                else:
                    st.error("❌ Download failed. The video might be private or unavailable.")
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error downloading video: {error_msg}")
                
                # Provide specific solutions based on error type
                if "rate-limit" in error_msg.lower() or "login required" in error_msg.lower():
                    st.markdown("""
                    **🔧 Quick Fixes:**
                    
                    1. **Make sure you're logged into Instagram in your browser**
                    2. **Try selecting a different browser in the settings above**
                    3. **Wait a few minutes and try again**
                    4. **Ensure the reel is public and accessible**
                    """)
                else:
                    st.info("💡 Tips: Make sure the URL is correct and the reel is publicly accessible")

    # Comprehensive troubleshooting guide
    with st.expander("🚨 Still having issues? Click here for detailed solutions"):
        st.markdown("""
        ### **Complete Solution Guide**
        
        **Method 1: Browser Cookies (Recommended)**
        - Make sure you're logged into Instagram in Chrome/Firefox/Edge
        - Select the correct browser type in the settings above
        - Keep "Use Browser Cookies" checked
        
        **Method 2: Manual Cookie Export**
        ```bash
        # Install cookie export extension
        # Export Instagram cookies as cookies.txt
        # Upload to your app directory
        ```
        
        **Method 3: Alternative Approaches**
        - Try different reel URLs
        - Use mobile user agents
        - Add delays between requests
        - Use residential proxies (for advanced users)
        
        **Common Issues:**
        - Private accounts cannot be downloaded
        - Age-restricted content may be blocked
        - Regional restrictions may apply
        - Instagram frequently changes their API
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Note: Only works with public Instagram Reels • Download for personal use only • Rate limits apply"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
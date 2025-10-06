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

# Initialize session state for download tracking
if 'download_count' not in st.session_state:
    st.session_state.download_count = 0
if 'last_reset_time' not in st.session_state:
    st.session_state.last_reset_time = datetime.now()
if 'cooldown_until' not in st.session_state:
    st.session_state.cooldown_until = None

def download_video(url, output_path):
    # Cookie file path - you'll need to provide this
    # You can get cookies by exporting from your browser
    cookie_file = "cookies.txt"  # Create this file with your Instagram cookies
    
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    # Add cookies if the file exists
    if os.path.exists(cookie_file):
        ydl_opts['cookiesfrombrowser'] = ('chrome',)  # or 'firefox', 'edge', etc.
    else:
        st.warning("⚠️ Using without cookies - may encounter rate limits")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

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
        if not ("instagram.com" in url and "/reel/" in url):
            st.error("Please enter a valid Instagram Reel URL")
        else:
            unique_id = str(uuid.uuid4())
            output_path = f"downloaded_video_{unique_id}.mp4"
            
            try:
                with st.spinner("🔄 Downloading your reel... This may take a few moments."):
                    download_video(url, output_path)
                
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
                    
            except Exception as e:
                st.error(f"❌ Error downloading video: {str(e)}")
                st.info("💡 Tips: Make sure the URL is correct and the reel is publicly accessible")

    # Instructions for cookies
    with st.expander("🔧 Having rate limit issues? Get better performance:"):
        st.markdown("""
        **To reduce rate limiting:**
        
        1. **Export cookies from your browser:**
           - Install a cookie export extension
           - Export Instagram cookies as `cookies.txt`
           - Upload the file to your app directory
        
        2. **Or use cookies automatically:**
           ```python
           ydl_opts['cookiesfrombrowser'] = ('chrome',)  # or 'firefox'
           ```
        
        This helps Instagram recognize you as a logged-in user.
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
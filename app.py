import streamlit as st
import yt_dlp
import os
import uuid
def download_video(url, output_path):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

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
    .input-container {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="main-header">📱 Instagram Reel Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download Instagram Reels as MP4 files instantly</div>', unsafe_allow_html=True)
    
    # URL input section without paste button
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
                    download_video(url, output_path)
                
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
                st.error(f"❌ Error downloading video: {str(e)}")
                st.info("💡 Tips: Make sure the URL is correct and the reel is publicly accessible")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Note: Only works with public Instagram Reels • Download for personal use only"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
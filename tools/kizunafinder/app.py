import streamlit as st
from streamlit_option_menu import option_menu
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta

# Google Custom Search API Configuration
API_KEY = "AIzaSyDiA0IAG6bEejxAt4ca0or2cbJfWZIVQB0"  # Replace with your API key
CSE_ID = "81126ca8728f54cc7"  # Replace with your CSE ID

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def extract_images_from_url(url):
    """
    Extract images from a webpage URL.
    Args:
        url (str): The URL to extract images from.
    Returns:
        str: URL of the first valid image found.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find images in various ways
        # 1. Look for og:image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        # 2. Look for twitter:image meta tag
        twitter_image = soup.find('meta', property='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
            
        # 3. Look for the first valid image in the content
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and is_valid_url(src):
                return src
                
        return None
    except Exception as e:
        st.warning(f"Could not extract image from {url}: {str(e)}")
        return None

def main():
    # Load CSS styles
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Calculate initial session time
    initial_session_time = time.time() - st.session_state.start_time

    # Add smooth real-time timer JavaScript
    st.markdown(f"""
        <script>
            // Store the initial session time
            let sessionStartTime = {st.session_state.start_time};
            
            function updateTimer() {{
                const now = new Date().getTime() / 1000;
                const elapsed = Math.floor(now - sessionStartTime);
                const hours = Math.floor(elapsed / 3600);
                const minutes = Math.floor((elapsed % 3600) / 60);
                const seconds = elapsed % 60;
                
                const timeString = String(hours).padStart(2, '0') + ':' + 
                                 String(minutes).padStart(2, '0') + ':' + 
                                 String(seconds).padStart(2, '0');
                
                // Update all timer elements
                document.querySelectorAll('.session-timer').forEach(element => {{
                    element.textContent = timeString;
                }});
            }}
            
            // Update timer every second
            setInterval(updateTimer, 1000);
            // Initial update
            updateTimer();
        </script>
    """, unsafe_allow_html=True)

    st.title("Social Media Search Application")
    st.write("Search for content on specific social media platforms using Google's Custom Search API.")

    # Display session time with smooth updates
    st.markdown(f"""
        <div style='text-align: right; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>
            <p style='margin: 0;'><strong>Session Time:</strong> <span class="session-timer">{format_time(initial_session_time)}</span></p>
        </div>
    """, unsafe_allow_html=True)

    # Create a container for the option menu
    menu_container = st.container()
    with menu_container:
        selected_option = option_menu(
            menu_title=None,
            options=["Home", "Facebook", "Twitter", "Instagram", "TikTok", "LinkedIn", "YouTube"],
            icons=["house", "facebook", "twitter", "instagram", "tiktok", "linkedin", "youtube"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#0e1117"},
            }
        )

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    if selected_option == "KizunaFinder":
        st.subheader("🔍 KizunaFinder OSINT Tool")
        kizunafinder_main()  # Run KizunaFinder tool
        return  # Stop further execution to prevent conflicts

    # Search Input
    query = st.text_input("Enter your search query:", "")

    if query:
        st.write(f"Showing results for: **{query}**")

        platform_sites = {
            "Facebook": "facebook.com",
            "Twitter": "twitter.com",
            "Instagram": "instagram.com",
            "TikTok": "tiktok.com",
            "LinkedIn": "linkedin.com",
            "YouTube": "youtube.com",
        }

        # Select Site for Platform-Specific Queries
        if selected_option == "Home":
            st.subheader("Search All Platforms")
            results = search_google_cse(query)
        else:
            st.subheader(f"{selected_option} Results")
            results = search_google_cse(query, site=platform_sites.get(selected_option, None))

        # Display Results
        if results:
            for result in results:
                st.markdown("""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                """, unsafe_allow_html=True)
                
                # Create two columns for content and media
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**{result['title']}**")
                    st.write(f"[{result['link']}]({result['link']})")
                    st.write(result["snippet"])
                
                with col2:
                    # Try to get image from the result link
                    image_url = result.get('image')
                    if not image_url:
                        image_url = extract_images_from_url(result['link'])
                    
                    if image_url and is_valid_url(image_url):
                        try:
                            st.image(image_url, use_column_width=True)
                        except Exception as e:
                            st.write("_Error loading image._")
                    else:
                        st.write("_No image available._")
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write("No results found.")

    # Footer
    st.markdown("""
        <div class='footer'>
            <div><strong>Osint Tool Pro</strong><br>Advanced OSINT platform for professionals.</div>
            <div><strong>Security & Privacy</strong><br>Anonymous searches. No data logged.</div>
            <div><strong>Resources</strong><br>Documentation<br>API Reference<br>Best Practices</div>
            <div><strong>Support</strong><br>Contact<br>Report Issues<br>Feature Requests</div>
        </div>
        <hr>
        <p style='text-align: center; font-size: 12px;'>
            ⚠️ <strong>Professional Use Only:</strong> For authorized investigations. Ensure legal compliance.<br>
            © 2025 Osint Tool Pro. Version 2.0.0 | Powered by <strong>ECLOGIC</strong>
        </p>
    """, unsafe_allow_html=True)

def search_google_cse(query, site=None):
    """
    Perform a Google Custom Search API query.
    Args:
        query (str): Search term.
        site (str): Specific site to search (e.g., tiktok.com).
    Returns:
        list: A list of search results (title, link, snippet, image).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": f"{query} site:{site}" if site else query,
        "key": API_KEY,
        "cx": CSE_ID,
        "num": 10,  # Number of results
        "safe": "active",  # Safe search
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = []
        
        if "items" in data:
            for item in data["items"]:
                # Try to get image from various sources
                image_url = None
                
                # 1. Try to get from pagemap
                if "pagemap" in item:
                    if "cse_image" in item["pagemap"]:
                        image_url = item["pagemap"]["cse_image"][0].get("src")
                    elif "metatags" in item["pagemap"]:
                        for meta in item["pagemap"]["metatags"]:
                            if "og:image" in meta:
                                image_url = meta["og:image"]
                            elif "twitter:image" in meta:
                                image_url = meta["twitter:image"]
                
                results.append({
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item.get("snippet", ""),
                    "image": image_url
                })
        return results
    except Exception as e:
        st.error(f"Error performing search: {str(e)}")
        return []

def is_valid_url(url):
    """
    Check if a URL is valid.
    Args:
        url (str): The URL to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except Exception:
        return False

if __name__ == "__main__":
    main()
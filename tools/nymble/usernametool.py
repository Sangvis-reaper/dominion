import streamlit as st
import requests
import re
from googlesearch import search
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat
from streamlit.components.v1 import html
import json
from datetime import datetime
import time

class UsernameOSINT:
    def __init__(self, username):
        self.username = username
        self.results = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\+?[1-9][0-9]{7,14}')

    def check_github(self):
        try:
            response = requests.get(f"https://api.github.com/users/{self.username}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "exists": True,
                    "name": data.get("name"),
                    "bio": data.get("bio"),
                    "location": data.get("location"),
                    "public_repos": data.get("public_repos"),
                    "followers": data.get("followers"),
                    "following": data.get("following"),
                    "profile_url": data.get("html_url"),
                    "email": data.get("email"),
                    "created_at": data.get("created_at"),
                    "last_updated": data.get("updated_at")
                }
        except Exception as e:
            return {"exists": False, "error": str(e)}
        return {"exists": False}

    def check_instagram(self):
        try:
            response = requests.get(f"https://www.instagram.com/{self.username}/", headers=self.headers)
            return {"exists": response.status_code == 200}
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def check_twitter(self):
        try:
            response = requests.get(f"https://twitter.com/{self.username}", headers=self.headers)
            return {"exists": response.status_code == 200}
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def check_linkedin(self):
        try:
            response = requests.get(f"https://www.linkedin.com/in/{self.username}/", headers=self.headers)
            return {"exists": response.status_code == 200}
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def search_whatsapp(self):
        found_numbers = set()
        search_query = f"{self.username} whatsapp contact"
        
        try:
            search_results = search(search_query, num_results=10)
            for url in search_results:
                try:
                    response = requests.get(url, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        numbers = self.phone_pattern.findall(response.text)
                        for number in numbers:
                            try:
                                parsed_number = parse(number)
                                if is_valid_number(parsed_number):
                                    formatted_number = format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL)
                                    found_numbers.add(formatted_number)
                            except:
                                continue
                except:
                    continue
        except Exception as e:
            return []
        return list(found_numbers)

    def search_emails(self):
        found_emails = set()
        search_query = f"{self.username} email contact"
        
        try:
            search_results = search(search_query, num_results=10)
            for url in search_results:
                try:
                    response = requests.get(url, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        emails = self.email_pattern.findall(response.text)
                        found_emails.update(emails)
                except:
                    continue
        except Exception as e:
            return []
        return list(found_emails)

    def save_results(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"osint_results_{self.username}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        return filename

def main():
    # Modern hero/info box styling
    st.markdown("""
        <style>
        .nymble-hero {
            background: linear-gradient(90deg, #e3f2fd 60%, #f8fafc 100%);
            border-radius: 18px;
            box-shadow: 0 4px 16px rgba(30,136,229,0.07);
            padding: 2.2rem 2rem 1.5rem 2rem;
            margin-bottom: 1.2rem;
            margin-top: 0.5rem;
        }
        .nymble-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #1976d2;
            margin-bottom: 0.2rem;
            letter-spacing: -1px;
        }
        .nymble-subtitle {
            font-size: 1.1rem;
            color: #333;
            margin-bottom: 0.7rem;
        }
        .nymble-features {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.1rem;
        }
        .nymble-pill {
            background: #fff;
            color: #1976d2;
            border-radius: 16px;
            padding: 0.25rem 0.9rem;
            font-size: 0.98rem;
            font-weight: 500;
            box-shadow: 0 1px 4px rgba(30,136,229,0.07);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .nymble-search-input {
            font-size: 1.1rem !important;
            border-radius: 8px !important;
            border: 1.5px solid #b3c6e0 !important;
            padding: 0.7rem 1rem !important;
            background: #fff !important;
            height: 48px !important;
            box-sizing: border-box !important;
        }
        .nymble-search-btn {
            background: linear-gradient(90deg, #1976d2 60%, #64b5f6 100%);
            color: #fff;
            font-weight: 700;
            font-size: 1.1rem;
            border-radius: 8px;
            border: none;
            padding: 0.7rem 1.5rem;
            cursor: pointer;
            transition: background 0.2s;
            height: 48px;
            margin-top: 0.7rem !important;
            margin-bottom: 0 !important;
            width: 100% !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nymble-search-btn:hover {
            background: linear-gradient(90deg, #1565c0 60%, #42a5f5 100%);
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    st.markdown("""
    <div class="nymble-hero">
        <div class="nymble-title">👤 Nymble <span style='font-size:1.1rem;font-weight:400;'>- Username OSINT Tool</span></div>
        <div class="nymble-subtitle">
            Discover social media profiles, emails, WhatsApp numbers, and analytics for any username across the web. Fast, private, and powerful OSINT for investigators and professionals.
        </div>
        <div class="nymble-features">
            <span class="nymble-pill">🔍 Social Media Profiles</span>
            <span class="nymble-pill">📧 Email Addresses</span>
            <span class="nymble-pill">📱 WhatsApp Numbers</span>
            <span class="nymble-pill">📊 Profile Analytics</span>
        </div>
    """, unsafe_allow_html=True)

    # --- SEARCH BAR (stacked: input then button) ---
    with st.form(key="nymble_search_form"):
        username = st.text_input("", placeholder="Enter username to search...", key="nymble_search_input")
        st.markdown("""
            <style>
            div[data-testid="stForm"] button {
                width: 100% !important;
                min-width: 0 !important;
                height: 48px !important;
                margin-top: 0.7rem !important;
                margin-bottom: 0 !important;
                border-radius: 8px !important;
                font-size: 1.1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        search_clicked = st.form_submit_button("🚀 Start Search")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- SEARCH OPTIONS ---
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header">⚙️ Search Options</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        search_social = st.checkbox("🌐 Search Social Media", value=True)
    with col2:
        search_contacts = st.checkbox("📱 Search Emails and WhatsApp", value=True)
    save_results = st.checkbox("💾 Save Results", value=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SEARCH LOGIC ---
    if search_clicked:
        if username:
            with st.spinner("🔍 Searching..."):
                osint = UsernameOSINT(username)
                results = {}

                if search_social:
                    st.markdown('<h2 class="sub-header">🌐 Social Media Profiles</h2>', unsafe_allow_html=True)
                    
                    # Create columns for social media results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        github = osint.check_github()
                        results['github'] = github
                        if github["exists"]:
                            st.markdown(f"""
                                <div class="success-box">
                                    <span class="platform-icon">🐙</span>
                                    <strong>GitHub profile found:</strong><br>
                                    <a href="{github['profile_url']}" target="_blank">View Profile</a>
                                </div>
                            """, unsafe_allow_html=True)
                            with st.expander("📊 GitHub Details"):
                                st.json(github)
                        else:
                            st.markdown('<div class="error-box"><span class="platform-icon">🐙</span> No GitHub profile found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        instagram = osint.check_instagram()
                        results['instagram'] = instagram
                        if instagram["exists"]:
                            st.markdown('<div class="success-box"><span class="platform-icon">📸</span> Instagram profile found.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box"><span class="platform-icon">📸</span> No Instagram profile found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        twitter = osint.check_twitter()
                        results['twitter'] = twitter
                        if twitter["exists"]:
                            st.markdown('<div class="success-box"><span class="platform-icon">🐦</span> Twitter profile found.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box"><span class="platform-icon">🐦</span> No Twitter profile found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        linkedin = osint.check_linkedin()
                        results['linkedin'] = linkedin
                        if linkedin["exists"]:
                            st.markdown('<div class="success-box"><span class="platform-icon">💼</span> LinkedIn profile found.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box"><span class="platform-icon">💼</span> No LinkedIn profile found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                if search_contacts:
                    st.markdown('<h2 class="sub-header">📱 Contact Information</h2>', unsafe_allow_html=True)
                    
                    # Create columns for contact results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown('<h3>📱 WhatsApp Numbers</h3>', unsafe_allow_html=True)
                        whatsapp_numbers = osint.search_whatsapp()
                        results['whatsapp'] = whatsapp_numbers
                        if whatsapp_numbers:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("**Potential WhatsApp numbers found:**")
                            for number in whatsapp_numbers:
                                st.markdown(f"📞 {number}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">No WhatsApp numbers found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown('<h3>📧 Email Addresses</h3>', unsafe_allow_html=True)
                        emails = osint.search_emails()
                        results['emails'] = emails
                        if emails:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("**Potential email addresses found:**")
                            for email in emails:
                                st.markdown(f"✉️ {email}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">No email addresses found.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                if save_results:
                    filename = osint.save_results(results)
                    st.markdown(f"""
                        <div class="success-box">
                            <span class="platform-icon">💾</span>
                            Results saved to <strong>{filename}</strong>
                        </div>
                    """, unsafe_allow_html=True)

        else:
            st.markdown('<div class="error-box">⚠️ Please enter a username to search.</div>', unsafe_allow_html=True)

    # Footer (copied from homepage for consistency)
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

if __name__ == "__main__":
    main()

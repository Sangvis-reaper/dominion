import streamlit as st
from streamlit_option_menu import option_menu
from tools.Hawker.main import Hawker
from pprint import pformat
import os

# Helper to capture print output
from io import StringIO
import sys

def capture_output(func, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        result = func(*args, **kwargs)
        output = mystdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output, result

def main():
    st.title("Hawker OSINT Tool (Streamlit Edition)")
    st.markdown("""
    <small>Advanced OSINT tool for investigative purposes. Use responsibly and legally.</small>
    """, unsafe_allow_html=True)

    hawker = Hawker()

    menu = [
        "Email Information",
        "Phone Information",
        "IP Information",
        "Camera Information",
        "Personal Information",
        "Bitcoin Information",
        "PyInstaller Information",
        "MAC Information",
        "VIN Information",
        "PDF Information",
        "Docx Information"
    ]

    svg_icons = {
        "Email Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="3 7 12 13 21 7"/></svg>',
        "Phone Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92V21a2 2 0 0 1-2.18 2A19.72 19.72 0 0 1 3 5.18 2 2 0 0 1 5 3h4.09a2 2 0 0 1 2 1.72c.13 1.13.37 2.23.72 3.28a2 2 0 0 1-.45 2.11l-1.27 1.27a16 16 0 0 0 6.29 6.29l1.27-1.27a2 2 0 0 1 2.11-.45c1.05.35 2.15.59 3.28.72A2 2 0 0 1 22 16.92z"/></svg>',
        "IP Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10A15.3 15.3 0 0 1 12 2z"/></svg>',
        "Camera Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2"/><circle cx="12" cy="14.5" r="3.5"/><path d="M22 7V5a2 2 0 0 0-2-2h-3.17a2 2 0 0 1-1.41-.59l-1.83-1.83a2 2 0 0 0-2.83 0l-1.83 1.83A2 2 0 0 1 7.17 3H4a2 2 0 0 0-2 2v2"/></svg>',
        "Personal Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4"/><path d="M5.5 21a10 10 0 0 1 13 0"/></svg>',
        "Bitcoin Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6h15v15H6z"/><path d="M9 9h6v6H9z"/><circle cx="12" cy="12" r="10"/></svg>',
        "PyInstaller Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M16 3v4a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V3"/></svg>',
        "MAC Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2"/><circle cx="12" cy="14.5" r="3.5"/></svg>',
        "VIN Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="7" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "PDF Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M16 3v4a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V3"/></svg>',
        "Docx Information": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M16 3v4a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V3"/></svg>',
    }

    # Create a dropdown with SVG icons
    def format_option(option):
        return f'<span style="display: flex; align-items: center; gap: 0.5em;">{svg_icons[option]}<span>{option}</span></span>'

    selected = st.selectbox(
        "Select Information Type:",
        options=menu,
        format_func=lambda x: x,
        index=0,
        key="hawker_selectbox"
    )

    # Show the selected option's SVG icon and label
    st.markdown(f'<div style="display: flex; align-items: center; gap: 0.5em; margin-bottom: 1em;">{svg_icons[selected]}<span style="font-size: 1.2em; font-weight: bold;">{selected}</span></div>', unsafe_allow_html=True)

    if selected == "Email Information":
        email = st.text_input("Enter Email Address")
        if st.button("Run Email OSINT", type="primary") and email:
            st.info("Running all email checks...")
            # Data Breach
            st.subheader("Data Breach")
            out, _ = capture_output(hawker.search_database, email)
            st.code(out or "No results.")
            # Ahmia
            st.subheader("Ahmia")
            out, _ = capture_output(hawker.extract_links_ahmia, email)
            st.code(out or "Done.")
            # Doxbin
            st.subheader("Doxbin")
            out, links = capture_output(hawker.doxbin_search, email)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            # Pastebin
            st.subheader("Pastebin")
            out, links = capture_output(hawker.pastebin_search, email)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            # Social Networks
            st.subheader("Social Networks")
            social_funcs = [
                hawker.check_github_email, hawker.picsart, hawker.pornhub, hawker.check_spotify_email,
                hawker.check_twitter_email, hawker.check_chess_email, hawker.check_duolingo_email,
                hawker.check_gravatar_email, hawker.check_pinterest_email, hawker.bitmoji, hawker.mewe,
                hawker.firefox, hawker.xnxx, hawker.xvideos, hawker.Patreon, hawker.Instagram
            ]
            for func in social_funcs:
                out, _ = capture_output(func, email)
                if out:
                    st.code(out)
            # Hudsonrock API
            st.subheader("Hudsonrock API")
            out, _ = capture_output(hawker.hudsonrock_api_email, email)
            st.code(out or "No results.")
            # WikiLeaks
            st.subheader("WikiLeaks")
            out, _ = capture_output(hawker.wikileaks_search, email)
            st.code(out or "No results.")

    elif selected == "Phone Information":
        phone = st.text_input("Enter Phone Number")
        if st.button("Run Phone OSINT", type="primary") and phone:
            st.info("Running all phone checks...")
            st.subheader("Ahmia")
            out, _ = capture_output(hawker.extract_links_ahmia, phone)
            st.code(out or "Done.")
            st.subheader("Doxbin")
            out, links = capture_output(hawker.doxbin_search, phone)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Pastebin")
            out, links = capture_output(hawker.pastebin_search, phone)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Phone Information")
            out, data = capture_output(hawker.get_phone_info, phone)
            if data:
                st.json(data)
            else:
                st.code(out or "No results.")

    elif selected == "IP Information":
        ip = st.text_input("Enter IP Address")
        if st.button("Run IP OSINT", type="primary") and ip:
            st.info("Running all IP checks...")
            st.subheader("Ahmia")
            out, _ = capture_output(hawker.extract_links_ahmia, ip)
            st.code(out or "Done.")
            st.subheader("Doxbin")
            out, links = capture_output(hawker.doxbin_search, ip)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Pastebin")
            out, links = capture_output(hawker.pastebin_search, ip)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Hudsonrock API")
            out, _ = capture_output(hawker.hudsonrock_api_ip, ip)
            st.code(out or "No results.")
            st.subheader("IP Geolocation")
            out, _ = capture_output(hawker.geolocation_ip, ip)
            st.code(out or "No results.")

    elif selected == "Camera Information":
        if st.button("Show Cameras", type="primary"):
            st.info("Decrypting and displaying camera URLs...")
            out, _ = capture_output(hawker.check_cameras)
            st.code(out or "No results.")

    elif selected == "Personal Information":
        fullname = st.text_input("Enter Full Name")
        if st.button("Run Personal OSINT", type="primary") and fullname:
            st.info("Running all personal info checks...")
            st.subheader("News (Algolia)")
            out, _ = capture_output(hawker.algolia, fullname)
            st.code(out or "No results.")
            st.subheader("Ahmia")
            out, _ = capture_output(hawker.extract_links_ahmia, fullname)
            st.code(out or "Done.")
            st.subheader("Doxbin")
            out, links = capture_output(hawker.doxbin_search, fullname)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Pastebin")
            out, links = capture_output(hawker.pastebin_search, fullname)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("PagesJaunes")
            out, links = capture_output(hawker.pagesjaunes_search, fullname)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("WhitePages")
            out, links = capture_output(hawker.whitepages_search, fullname)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")

    elif selected == "Bitcoin Information":
        bitcoin = st.text_input("Enter Bitcoin Address")
        if st.button("Run Bitcoin OSINT", type="primary") and bitcoin:
            st.info("Running all bitcoin checks...")
            st.subheader("Ahmia")
            out, _ = capture_output(hawker.extract_links_ahmia, bitcoin)
            st.code(out or "Done.")
            st.subheader("Doxbin")
            out, links = capture_output(hawker.doxbin_search, bitcoin)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("Pastebin")
            out, links = capture_output(hawker.pastebin_search, bitcoin)
            if links:
                for link in links:
                    st.write(link)
            else:
                st.code(out or "No results.")
            st.subheader("BlockChain")
            out, _ = capture_output(hawker.get_bitcoin_info, bitcoin)
            st.code(out or "No results.")

    elif selected == "PyInstaller Information":
        file = st.text_input("Enter Path to .exe File")
        if st.button("Analyze PE File", type="primary") and file:
            if os.path.exists(file):
                out, _ = capture_output(hawker.get_pe_info, file)
                st.code(out or "No results.")
            else:
                st.error("File does not exist.")

    elif selected == "MAC Information":
        mac = st.text_input("Enter MAC Address")
        if st.button("Lookup MAC", type="primary") and mac:
            out, result = capture_output(hawker.mac_address_lookup, mac)
            if isinstance(result, dict):
                st.json(result)
            else:
                st.code(out or "No results.")

    elif selected == "VIN Information":
        vin = st.text_input("Enter VIN Number")
        if st.button("Lookup VIN", type="primary") and vin:
            out, _ = capture_output(hawker.get_vehicle_info, vin)
            st.code(out or "No results.")

    elif selected == "PDF Information":
        pdf_path = st.text_input("Enter Path to PDF File")
        if st.button("Extract PDF Metadata", type="primary") and pdf_path:
            if os.path.exists(pdf_path):
                out, _ = capture_output(hawker.extract_pdf_metadata, pdf_path)
                st.code(out or "No results.")
            else:
                st.error("File does not exist.")

    elif selected == "Docx Information":
        docx_path = st.text_input("Enter Path to DOCX File")
        if st.button("Extract DOCX Metadata", type="primary") and docx_path:
            if os.path.exists(docx_path):
                metadata = hawker.extract_metadata(docx_path)
                st.json(metadata)
            else:
                st.error("File does not exist.")

    # Footer (same as KizunaFinder)
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
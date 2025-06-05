import streamlit as st
from tools.kizunafinder.app import main as kizunafinder_main
from tools.socialpulse.app import main as socialpulse_main
from tools.telegram_checker.app import main as telegram_checker_main
from tools.waybacktweets.app import main as waybacktweets_main
from tools.holeheweb.holeheweb import email_checker_main
from tools.GHunt.app import render_ghunt_interface
from tools.sherlock.sherlockweb import username_checker_main
from tools.nymble.usernametool import main as usernametool_main
from tools.Hawker.app import main as hawker_main
import time
from datetime import datetime, timedelta
import asyncio

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def homepage():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Initialize session states
    if 'show_custom_search' not in st.session_state:
        st.session_state.show_custom_search = False
    if 'show_dashboard' not in st.session_state:
        st.session_state.show_dashboard = True
    if 'show_phone_validator' not in st.session_state:
        st.session_state.show_phone_validator = False
    if 'show_telegram_checker' not in st.session_state:
        st.session_state.show_telegram_checker = False
    if 'show_wayback_tweets' not in st.session_state:
        st.session_state.show_wayback_tweets = False
    if 'show_email_checker' not in st.session_state:
        st.session_state.show_email_checker = False
    if 'show_ghunt' not in st.session_state:
        st.session_state.show_ghunt = False
    if 'show_sherlock' not in st.session_state:
        st.session_state.show_sherlock = False
    if 'show_username_tool' not in st.session_state:
        st.session_state.show_username_tool = False
    if 'show_hawker' not in st.session_state:
        st.session_state.show_hawker = False
    if 'show_gvision' not in st.session_state:
        st.session_state.show_gvision = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

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

    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        
        # Dashboard button at the top
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = True
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()

        # Phone Number section
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Phone Number</div>
        """, unsafe_allow_html=True)
        
        # Phone Number Validator button
        if st.button("📱 Phone Number Validator", use_container_width=True):
            st.session_state.show_phone_validator = True
            st.session_state.show_dashboard = False
            st.session_state.show_custom_search = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        # Telegram Checker button
        if st.button("📲 Telegram Checker", use_container_width=True):
            st.session_state.show_telegram_checker = True
            st.session_state.show_dashboard = False
            st.session_state.show_custom_search = False
            st.session_state.show_phone_validator = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Username section
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Username</div>
        """, unsafe_allow_html=True)
        
        # Sherlock Username Finder button
        if st.button("🔍 Sherlock Username Finder", use_container_width=True):
            st.session_state.show_sherlock = True
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        # UsernameOSINT Tool button
        if st.button("👤 Nymble", use_container_width=True):
            st.session_state.show_username_tool = True
            st.session_state.show_sherlock = False
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Social Media section
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Social Media</div>
        """, unsafe_allow_html=True)
        
        # Custom Search Engine button
        if st.button("🔎 Custom Search Engine", use_container_width=True):
            st.session_state.show_custom_search = True
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        # Wayback Tweets button
        if st.button("🕰️ Wayback Tweets", use_container_width=True):
            st.session_state.show_wayback_tweets = True
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Information Lookup section
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Information Lookup</div>
        """, unsafe_allow_html=True)
        
        # Hawker OSINT Tool button
        if st.button("🦅 Hawker OSINT Tool", use_container_width=True):
            st.session_state.show_hawker = True
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_gvision = False
            st.rerun()
        
        # GVision Tool button
        if st.button("📷 GVision Reverse Image Search", use_container_width=True):
            st.session_state.show_gvision = True
            st.session_state.show_hawker = False
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_email_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Email section
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Email</div>
        """, unsafe_allow_html=True)
        
        # Email Checker button
        if st.button("📧 Email Checker", use_container_width=True):
            st.session_state.show_email_checker = True
            st.session_state.show_wayback_tweets = False
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_ghunt = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        # GHunt button
        if st.button("🔍 GHunt", use_container_width=True):
            st.session_state.show_ghunt = True
            st.session_state.show_email_checker = False
            st.session_state.show_wayback_tweets = False
            st.session_state.show_custom_search = False
            st.session_state.show_dashboard = False
            st.session_state.show_phone_validator = False
            st.session_state.show_telegram_checker = False
            st.session_state.show_sherlock = False
            st.session_state.show_username_tool = False
            st.session_state.show_hawker = False
            st.session_state.show_gvision = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Session Timer with smooth updates
        st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">Session Info</div>
                <div style='text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px;'>
                    <p style='margin: 0;'><strong>Session Time:</strong><br><span class="session-timer">{}</span></p>
                </div>
            </div>
        """.format(format_time(initial_session_time)), unsafe_allow_html=True)
        
        # Logout button at bottom
        st.markdown("<div class='sidebar-logout'>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("You have been logged out.")
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Check which tool to show
    if st.session_state.show_custom_search:
        kizunafinder_main()
        return
    elif st.session_state.show_phone_validator:
        socialpulse_main()
        return
    elif st.session_state.show_telegram_checker:
        asyncio.run(telegram_checker_main())
        return
    elif st.session_state.show_wayback_tweets:
        waybacktweets_main()
        return
    elif st.session_state.show_email_checker:
        email_checker_main()
        return
    elif st.session_state.show_ghunt:
        render_ghunt_interface()
        return
    elif st.session_state.show_sherlock:
        username_checker_main()
        return
    elif st.session_state.show_username_tool:
        usernametool_main()
        return
    elif st.session_state.get('show_hawker', False):
        hawker_main()
        return
    elif st.session_state.get('show_gvision', False):
        from tools.gvision.app import main as gvision_main
        gvision_main()
        return

    # Regular homepage content (Dashboard)
    st.markdown("""
        <div class="header">
            <div>
                <h2>🔎 <span class='highlight'>Osint Tool Pro</span></h2>
                <p>Enterprise OSINT Intelligence Platform</p>
            </div>
            <div class="session-info">
                <p>Logged in as <strong>admin</strong></p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Rest of the homepage content
    st.markdown("""
        <div class="metrics">
            <p>🔍 Total Searches: <strong>0</strong></p>
            <p>📈 Success Rate: <strong>0.0%</strong></p>
            <p>🛡 Platforms Checked: <strong>0</strong></p>
        </div>
    """, unsafe_allow_html=True)

    # Intelligence Dashboard Box
    st.markdown("""
        <div class="info-box">
            <h2>🧠 Intelligence Dashboard</h2>
            <p>Welcome to Osint Tool Pro - Your comprehensive OSINT platform</p>
        </div>
    """, unsafe_allow_html=True)

    # Platform Capabilities Box
    st.markdown("<h2>🚀 Platform Capabilities</h2>", unsafe_allow_html=True)
    
    # Create three equal columns
    col1, col2, col3 = st.columns(3)
    
    # Domain Intelligence Card
    with col1:
        st.markdown("""
            <div class="capability-card">
                <div>
                    <h3>🌐 Domain Intelligence</h3>
                    <p>Comprehensive domain analysis including WHOIS, DNS, security assessment, and infrastructure mapping.</p>
                </div>
                <p>Platforms: <strong>25+</strong><br>Accuracy: <strong>99.9%</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    # Identity Investigation Card
    with col2:
        st.markdown("""
            <div class="capability-card">
                <div>
                    <h3>👤 Identity Investigation</h3>
                    <p>Multi-platform username and personal information discovery across social networks and professional platforms.</p>
                </div>
                <p>Platforms: <strong>50+</strong><br>Accuracy: <strong>95.2%</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    # Communication Analysis Card
    with col3:
        st.markdown("""
            <div class="capability-card">
                <div>
                    <h3>📱 Communication Analysis</h3>
                    <p>Phone number intelligence, messaging platform investigation, and communication pattern analysis.</p>
                </div>
                <p>Platforms: <strong>15+</strong><br>Accuracy: <strong>97.8%</strong></p>
            </div>
        """, unsafe_allow_html=True)

    # Quick Start Guide Box
    st.markdown("""
        <div class="quick-start-box">
            <h2>📌 Quick Start Guide</h2>
            <p>1. Select Tool: Choose the appropriate intelligence tool from the sidebar.</p>
            <p>2. Enter Data: Input the target information (domain, username, email, etc).</p>
            <p>3. Run Analysis: Execute the investigation and monitor progress.</p>
            <p>4. Review Results: Analyze findings through visualizations.</p>
            <p>5. Export Reports: Download reports in JSON, CSV, or HTML formats.</p>
        </div>
    """, unsafe_allow_html=True)

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

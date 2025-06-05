import streamlit as st
import subprocess
import re
import os
import time
from datetime import datetime, timedelta

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def is_valid_email(email):
    """Validate email format"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_tool_installed(tool_name):
    """Check if a tool is installed in the system"""
    return subprocess.call(["which", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def run_holehe_check(email):
    """Run holehe check and return results"""
    try:
        result = subprocess.run(
            ['holehe', email],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error("Error executing Holehe command.")
        st.text(e.output)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def email_checker_main():
    # Initialize session state for timing
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    # Calculate session time
    initial_session_time = time.time() - st.session_state.start_time

    # Add timer JavaScript
    st.markdown(f"""
        <script>
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
                document.querySelectorAll('.session-timer').forEach(element => {{
                    element.textContent = timeString;
                }});
            }}
            setInterval(updateTimer, 1000);
            updateTimer();
        </script>
    """, unsafe_allow_html=True)

    # Main interface
    st.title("Email Checker")
    st.write("Check which sites are linked to a specific email address using Holehe.")

    # Session timer
    st.markdown(f"""
        <div style='text-align: right; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>
            <p style='margin: 0;'><strong>Session Time:</strong> <span class="session-timer">{format_time(initial_session_time)}</span></p>
        </div>
    """, unsafe_allow_html=True)

    # Check if Holehe is installed
    if not is_tool_installed("holehe"):
        st.error("Holehe is not installed or not available in the system PATH. Please install it and try again.")
        return

    # Create results directory
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    # Email input
    email = st.text_input("Enter the email address to check:", placeholder="example@example.com").strip()

    if st.button("Check Email"):
        if email and is_valid_email(email):
            st.write(f"Checking accounts for email: {email}")
            
            with st.spinner("Processing..."):
                # Run holehe check
                result = run_holehe_check(email)
                
                if result:
                    # Save results
                    output_file = os.path.join(results_dir, f"{email}_holehe_result.txt")
                    with open(output_file, 'w') as f:
                        f.write(result)
                    
                    # Display results
                    st.success("Check completed successfully!")
                    st.subheader("Results:")
                    st.text(result)
                    
                    # Download button
                    st.download_button(
                        label="Download Results",
                        data=result,
                        file_name=os.path.basename(output_file),
                        mime="text/plain",
                    )
        else:
            st.error("Please enter a valid email address.")

    # Footer
    st.markdown("""
        <div class='footer'>
            <div><strong>Email Checker Pro</strong><br>Advanced email verification platform.</div>
            <div><strong>Security & Privacy</strong><br>Anonymous checks. No data logged.</div>
            <div><strong>Resources</strong><br>Documentation<br>API Reference</div>
            <div><strong>Support</strong><br>Contact<br>Report Issues</div>
        </div>
        <hr>
        <p style='text-align: center; font-size: 12px;'>
            ⚠️ <strong>Professional Use Only:</strong> For authorized investigations.<br>
            © 2025 Email Checker Pro | Powered by <strong>ECLOGIC</strong>
        </p>
    """, unsafe_allow_html=True)



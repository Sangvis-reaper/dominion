import streamlit as st
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys

# Add the tools directory to the Python path
tools_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if tools_dir not in sys.path:
    sys.path.append(tools_dir)

from telegram_checker.telegram_checker import TelegramChecker, validate_phone_number, validate_username

# Initialize session states
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def save_results(results, identifier_type):
    """Save results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get the telegram_checker directory path
    telegram_checker_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    results_dir = telegram_checker_dir / "results"
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / f"results_{identifier_type}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return output_file

def display_results(results):
    """Display results in a formatted way"""
    for identifier, data in results.items():
        with st.expander(f"Results for {identifier}"):
            if "error" in data:
                st.error(f"Error: {data['error']}")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Basic Information**")
                    st.write(f"Name: {data.get('first_name', '')} {data.get('last_name', '')}")
                    st.write(f"Username: @{data.get('username', 'No username')}")
                    st.write(f"Phone: {data.get('phone', 'Not available')}")
                    st.write(f"Last Seen: {data.get('last_seen', 'Unknown')}")
                
                with col2:
                    st.markdown("**Account Status**")
                    st.write(f"Premium: {'Yes' if data.get('premium') else 'No'}")
                    st.write(f"Verified: {'Yes' if data.get('verified') else 'No'}")
                    st.write(f"Fake: {'Yes' if data.get('fake') else 'No'}")
                    st.write(f"Bot: {'Yes' if data.get('bot') else 'No'}")
                
                if data.get('profile_photos'):
                    st.markdown("**Profile Photos**")
                    cols = st.columns(min(3, len(data['profile_photos'])))
                    for i, photo_path in enumerate(data['profile_photos']):
                        if os.path.exists(photo_path):
                            with cols[i % 3]:
                                st.image(photo_path, use_column_width=True)

async def process_input(checker, input_type, input_data):
    """Process input data and return results"""
    if input_type == "phone":
        return await checker.process_phones(input_data)
    else:
        return await checker.process_usernames(input_data)

async def main():
    try:
        # Load CSS styles
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        st.title("📲 Telegram Account Checker")

        # Initialize Telegram Checker
        checker = TelegramChecker()
        
        # Sidebar for API configuration
        with st.sidebar:
            st.markdown("### API Configuration")
            api_id = st.text_input("API ID", type="password")
            api_hash = st.text_input("API Hash", type="password")
            phone = st.text_input("Your Phone Number (with country code)")
            
            if st.button("Save API Configuration"):
                if api_id and api_hash and phone:
                    try:
                        checker.config['api_id'] = int(api_id)
                        checker.config['api_hash'] = api_hash
                        checker.config['phone'] = validate_phone_number(phone)
                        checker.save_config()
                        st.success("API configuration saved!")
                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")
                else:
                    st.error("Please fill in all fields")

        # Main content
        st.markdown("### Check Telegram Accounts")
        
        # Input type selection
        input_type = st.radio(
            "Select input type",
            ["Phone Numbers", "Usernames"],
            horizontal=True
        )
        
        # Input method selection
        input_method = st.radio(
            "Select input method",
            ["Manual Input", "File Upload"],
            horizontal=True
        )
        
        if input_method == "Manual Input":
            input_data = st.text_area(
                f"Enter {input_type.lower()} (one per line or comma-separated)",
                help="You can enter multiple values separated by commas or new lines"
            )
            if input_data:
                input_data = [item.strip() for item in input_data.replace('\n', ',').split(',') if item.strip()]
        else:
            uploaded_file = st.file_uploader(f"Upload a file containing {input_type.lower()}", type=['txt'])
            if uploaded_file:
                input_data = [line.strip() for line in uploaded_file.getvalue().decode().splitlines() if line.strip()]
        
        if st.button("Start Checking") and 'input_data' in locals():
            try:
                # Initialize the checker
                await checker.initialize()
                
                # Process the input
                with st.spinner("Checking accounts..."):
                    results = await process_input(
                        checker,
                        "phone" if input_type == "Phone Numbers" else "username",
                        input_data
                    )
                
                # Save results
                output_file = save_results(
                    results,
                    "phones" if input_type == "Phone Numbers" else "usernames"
                )
                
                # Display results
                st.success(f"Results saved to {output_file}")
                display_results(results)
                
                # Download button for results
                with open(output_file, 'r') as f:
                    st.download_button(
                        label="📥 Download Results",
                        data=f,
                        file_name=output_file.name,
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

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
    except Exception as e:
        st.error(f"An error occurred in the main function: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
import streamlit as st
import requests
import pandas as pd
import json
import io
import time
from datetime import datetime, timedelta
import os

# Replace with your Neutrino API credentials
USER_ID = "Tohka"
API_KEY = "On2I9wPkS2aJYflMX99umTM0XfbTFL4LH3JoHpZVc0gxuV7n"

# API endpoint
url = "https://neutrinoapi.net/phone-validate"

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def phone_validation_app():
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

    st.title("📱 Phone Number Validator")

    # Display session time
    st.markdown(f"""
        <div style='text-align: right; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>
            <p style='margin: 0;'><strong>Session Time:</strong> <span class="session-timer">{format_time(initial_session_time)}</span></p>
        </div>
    """, unsafe_allow_html=True)

    # User input fields
    number = st.text_input("Enter the phone number (e.g., +6495552000):")

    # Button to trigger validation
    if st.button("✅ Validate Phone Number"):
        if number:
            params = {
                "number": number,
            }

            headers = {
                "User-ID": USER_ID,
                "API-Key": API_KEY
            }

            # Make the POST request
            response = requests.post(url, headers=headers, data=params)

            if response.status_code == 200:
                data = response.json()

                # Rearrange the results
                rearranged_data = {
                    "✔️ Valid": data.get("valid"),
                    "📞 Type": data.get("type"),
                    "🌍 Country": data.get("country"),
                    "📍 Location": data.get("location"),
                    "🔢 International Number": data.get("international-number"),
                    "🔢 Local Number": data.get("local-number"),
                    "🇨🇺 Country Code": data.get("country-code"),
                    "💱 Currency Code": data.get("currency-code"),
                    "📡 International Calling Code": data.get("international-calling-code"),
                    "📱 Is Mobile": data.get("is-mobile"),
                    "📶 Carrier Service Provider": data.get("prefix-network")
                }

                # Display rearranged data in a styled box
                st.subheader("Phone Validation Results:")
                st.markdown(
                    """<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    """ + "<br>".join([f"<b>{key}:</b> {value}" for key, value in rearranged_data.items()]) + "</div>",
                    unsafe_allow_html=True
                )

                # Check additional country details from CSV
                current_dir = os.path.dirname(os.path.abspath(__file__))
                csv_file = os.path.join(current_dir, "countries", "countries.csv")
                try:
                    country_data = pd.read_csv(csv_file, delimiter=";")
                    country_info = country_data[country_data['Country Name'] == data.get("country")]

                    if not country_info.empty:
                        st.subheader("Additional Country Details:")
                        st.markdown(
                            """<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            """ + "<br>".join([f"<b>{col}:</b> {country_info.iloc[0][col]}" for col in country_info.columns]) + "</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("No additional details found for this country in the CSV file.")

                except FileNotFoundError:
                    st.error(f"Country details CSV file not found at: {csv_file}")
                except Exception as e:
                    st.error(f"Error reading country details: {str(e)}")

                # Convert results to CSV format
                df = pd.DataFrame([rearranged_data])
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, sep=';')
                csv_data = csv_buffer.getvalue()

                # Add some space before the download button
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name="phone_validation_results.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        else:
            st.warning("Please enter a valid phone number.")

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

# Define the main function for integration
def main():
    phone_validation_app()

if __name__ == "__main__":
    main()
import base64
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from waybacktweets import WaybackTweets, TweetsParser, TweetsExporter
from waybacktweets.api.visualize import HTMLTweetsVisualizer
from waybacktweets.config import FIELD_OPTIONS, config

def main():
    # ----- Streamlit App Title -----
    st.title("Wayback Tweets")
    st.write("Easily explore and download archived tweets from Twitter/X  using the Wayback Machine.")

    # ----- User Inputs -----
    username = st.text_input("Enter the Twitter username:", placeholder="e.g., elonmusk")
    start_date = st.date_input("Start date", help="Start date for filtering archived tweets.")
    end_date = st.date_input("End date", help="End date for filtering archived tweets.")

    # Optional: Filter by archived status codes
    status_codes_filter = st.multiselect(
        "Filter by archived status codes (optional):",
        options=["200", "404", "500", "403"],
        help="Select status codes to filter tweets. Leave empty to skip filtering."
    )

    # ----- Query Button -----
    if st.button("Query Tweets"):
        if not username:
            st.error("Please enter a valid Twitter username.")
        elif start_date > end_date:
            st.error("The end date must be after the start date.")
        else:
            st.info("Fetching archived tweets. Please wait...")
            try:
                collapse = None
                matchtype = None
                timestamp_from = datetime.combine(start_date, datetime.min.time())
                timestamp_to = datetime.combine(end_date, datetime.max.time())

                response = WaybackTweets(
                    username,
                    collapse,
                    timestamp_from,
                    timestamp_to,
                    limit=None,
                    offset=None,
                    matchtype=None
                )
                archived_tweets = response.get()

                if archived_tweets:
                    parser = TweetsParser(archived_tweets, username, FIELD_OPTIONS)
                    parsed_tweets = parser.parse()

                    exporter = TweetsExporter(parsed_tweets, username, FIELD_OPTIONS)
                    df = exporter.dataframe
                    file_name = exporter.filename

                    df["timestamp"] = pd.to_datetime(df["archived_timestamp"], errors="coerce")

                    # Filter by date range again (safe-guard)
                    filtered_df = df[
                        (df["timestamp"] >= pd.Timestamp(start_date)) &
                        (df["timestamp"] <= pd.Timestamp(end_date))
                    ]

                    # Filter by status codes if selected
                    if status_codes_filter:
                        filtered_df = filtered_df[
                            filtered_df["archived_statuscode"].isin(status_codes_filter)
                        ]

                    if not filtered_df.empty:
                        st.success(f"Found {len(filtered_df)} tweets in the specified range.")
                        st.write("Filtered Archived Tweets:")
                        st.dataframe(filtered_df)

                        # Download options in a dropdown
                        download_format = st.selectbox(
                            "Select download format:",
                            options=["Select format...", "CSV", "JSON", "HTML"],
                            help="Choose the format to download the tweets"
                        )

                        if download_format != "Select format...":
                            # Create columns for download button
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                if download_format == "CSV":
                                    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
                                    st.download_button(
                                        label="📥 Download",
                                        data=csv_data,
                                        file_name=f"{username}_archived_tweets.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                elif download_format == "JSON":
                                    json_data = filtered_df.to_json(orient="records", lines=False)
                                    b64_json = base64.b64encode(json_data.encode()).decode()
                                    href_json = f"data:file/json;base64,{b64_json}"
                                    st.markdown(
                                        f'<a href="{href_json}" download="{file_name}.json"><button style="width: 100%; background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer;">📥 Download</button></a>',
                                        unsafe_allow_html=True,
                                    )
                                elif download_format == "HTML":
                                    json_data = filtered_df.to_json(orient="records", lines=False)
                                    html = HTMLTweetsVisualizer(username, json_data)
                                    html_content = html.generate()
                                    b64_html = base64.b64encode(html_content.encode()).decode()
                                    href_html = f"data:text/html;base64,{b64_html}"
                                    st.markdown(
                                        f'<a href="{href_html}" download="{file_name}.html"><button style="width: 100%; background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer;">📥 Download</button></a>',
                                        unsafe_allow_html=True,
                                    )
                            
                            with col2:
                                st.markdown(f"**Selected format:** {download_format}")
                                st.markdown(f"**File name:** {username}_archived_tweets.{download_format.lower()}")
                    else:
                        st.warning("No tweets match the specified filters.")
                else:
                    st.warning("No archived tweets found for the given username.")

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

# Run the app
if __name__ == "__main__":
    main()
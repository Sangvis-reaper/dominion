import streamlit as st
import os
import json
import asyncio
import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberBannedError, UsernameInvalidError
from telethon import functions, types

# Define the base directory for storage inside `/home/elk/tools/tele/`
BASE_DIR = "/home/elk/tools/tele"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SESSION_FILE = os.path.join(BASE_DIR, "session_name.session")

def telegram_scraper_main():
    """ Streamlit App for Telegram Phone & Username Checker """

    # Load environment variables
    load_dotenv()

    # Streamlit app title
    st.title("Telegram Phone Checker")

    # Load API credentials from environment variables
    api_id = os.getenv("APP_API_ID", "1807430")
    api_hash = os.getenv("APP_API_HASH", "ee09343af2a246aeb9c130c9e74a0179")

    # Ensure the results directory exists before saving files
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Helper function to serialize JSON safely
    def json_serializer(obj):
        if isinstance(obj, bytes):
            return obj.decode("utf-8", "ignore")  # Decode bytes to string
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # Function to check a phone number
    async def check_phone(phone):
        async with TelegramClient(SESSION_FILE, api_id, api_hash) as client:
            try:
                # 1. Add the phone number as a contact
                result = await client(functions.contacts.ImportContactsRequest(
                    contacts=[types.InputPhoneContact(client_id=0, phone=phone, first_name="Temp", last_name="User")]
                ))
                if result.users:
                    user = result.users[0]
                    # 2. Remove the contact immediately
                    await client(functions.contacts.DeleteContactsRequest(id=[user.id]))
                    # Extract real first and last name and username from Telegram profile
                    user_info = user.to_dict()
                    user_info['first_name'] = user.first_name
                    user_info['last_name'] = user.last_name
                    user_info['username'] = user.username
                    return user_info
                else:
                    return {"error": "No user found for this phone number"}
            except PhoneNumberBannedError:
                return {"error": "Phone number is banned"}
            except Exception as e:
                return {"error": str(e)}

    # Function to check a username
    async def check_username(username):
        async with TelegramClient(SESSION_FILE, api_id, api_hash) as client:
            try:
                user = await client.get_entity(username)
                return user.to_dict()
            except UsernameInvalidError:
                return {"error": "Invalid username"}
            except Exception as e:
                return {"error": str(e)}

    # Options selection
    option = st.selectbox("Select an option", [
        "Check phone number",
        "Check phone numbers from file",
        "Check username",
        "Check usernames from file",
        "Clear saved credentials"
    ])

    if option == "Check phone number":
        phone = st.text_input("Enter phone number (with country code)")
        if st.button("Check Telegram Account"):
            result = asyncio.run(check_phone(phone))
            st.json(result)
            file_path = os.path.join(RESULTS_DIR, f"{phone.replace('+', '')}.json")  # Save in `/home/elk/tools/tele/results/`
            with open(file_path, "w") as f:
                json.dump(result, f, indent=4, default=json_serializer)
            st.success(f"Result saved successfully at {file_path}!")

    elif option == "Check phone numbers from file":
        uploaded_file = st.file_uploader("Upload a file containing phone numbers", type=["txt"])
        if uploaded_file and st.button("Check Numbers"):
            phone_numbers = uploaded_file.read().decode("utf-8").splitlines()
            results = {}
            for phone in phone_numbers:
                results[phone] = asyncio.run(check_phone(phone))
            st.json(results)
            file_path = os.path.join(RESULTS_DIR, "phones_results.json")
            with open(file_path, "w") as f:
                json.dump(results, f, indent=4, default=json_serializer)
            st.success(f"Results saved successfully at {file_path}!")

    elif option == "Check username":
        username = st.text_input("Enter Telegram username")
        if st.button("Check Telegram Account"):
            result = asyncio.run(check_username(username))
            st.json(result)
            file_path = os.path.join(RESULTS_DIR, f"{username}.json")
            with open(file_path, "w") as f:
                json.dump(result, f, indent=4, default=json_serializer)
            st.success(f"Result saved successfully at {file_path}!")

    elif option == "Check usernames from file":
        uploaded_file = st.file_uploader("Upload a file containing usernames", type=["txt"])
        if uploaded_file and st.button("Check Usernames"):
            usernames = uploaded_file.read().decode("utf-8").splitlines()
            results = {}
            for username in usernames:
                results[username] = asyncio.run(check_username(username))
            st.json(results)
            file_path = os.path.join(RESULTS_DIR, "usernames_results.json")
            with open(file_path, "w") as f:
                json.dump(results, f, indent=4, default=json_serializer)
            st.success(f"Results saved successfully at {file_path}!")

    elif option == "Clear saved credentials":
        if st.button("Clear Session Data"):
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
                st.success("Session data cleared!")
            else:
                st.warning("No session data found.")

 # Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. Developed by ECLOGIC.
    """)

if __name__ == "__main__":
    telegram_scraper_main()

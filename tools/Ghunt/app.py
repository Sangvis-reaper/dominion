import streamlit as st
import subprocess
import sys
import os
from typing import Optional, Dict, Any

# Set GHunt path (adjusted to correct directory)
GHUNT_PATH = os.path.join(os.path.dirname(__file__), "main.py")

# ----------------- CONFIGURATION -----------------
APP_CONFIG = {
    "title": "GHunt OSINT",
    "description": "This application provides a web interface for GHunt, allowing users to analyze Google account information based on an email address.",
    "tasks": {
        "Email Information": {
            "command": "ghunt email",
            "input_label": "Enter the email address to investigate:",
            "placeholder": "example@gmail.com",
            "icon": "📧"
        },
        "Gaia ID Information": {
            "command": "ghunt gaia",
            "input_label": "Enter the Gaia ID to investigate:",
            "placeholder": "123456789",
            "icon": "🆔"
        },
        "Drive Information": {
            "command": "ghunt drive",
            "input_label": "Enter the Drive file or folder URL:",
            "placeholder": "https://drive.google.com/...",
            "icon": "📁"
        },
        "Geolocate BSSID": {
            "command": "ghunt geolocate",
            "input_label": "Enter the BSSID to geolocate:",
            "placeholder": "00:11:22:33:44:55",
            "icon": "📍"
        }
    }
}

# ----------------- UTILITY FUNCTIONS -----------------
def run_ghunt_command(command: str) -> str:
    """Run a GHunt command safely and capture the output."""
    try:
        if not os.path.exists(GHUNT_PATH):
            return f"Error: GHunt script not found at {GHUNT_PATH}"
        
        result = subprocess.run(
            command.split(),
            text=True,
            capture_output=True,
            cwd=os.path.dirname(GHUNT_PATH)
        )
        
        if result.returncode != 0:
            return f"Error executing command: {result.stderr}"
        
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return f"Error executing command: {str(e)}"

# ----------------- UI COMPONENTS -----------------
def render_header():
    """Render the main header section."""
    st.title(APP_CONFIG["title"])
    st.write(APP_CONFIG["description"])

def render_task_selector() -> str:
    """Render the task selection interface in the main page."""
    st.markdown("### Select Analysis Type")
    
    # Create columns for task selection
    cols = st.columns(2)
    selected_task = None
    
    # Create task selection cards
    for i, (task_name, task_config) in enumerate(APP_CONFIG["tasks"].items()):
        with cols[i % 2]:
            st.markdown(f"""
                <div style='padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 20px;'>
                    <h3 style='margin: 0;'>{task_config['icon']} {task_name}</h3>
                    <p style='color: #666; margin: 5px 0;'>{task_config['input_label']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {task_name}", key=f"btn_{task_name}", use_container_width=True):
                selected_task = task_name
    
    return selected_task

def render_task_interface(task: str):
    """Render the interface for the selected task."""
    task_config = APP_CONFIG["tasks"][task]
    
    st.markdown(f"### {task_config['icon']} {task}")
    user_input = st.text_input(
        task_config["input_label"],
        placeholder=task_config["placeholder"]
    )
    
    if st.button(f"Run GHunt on {task}", use_container_width=True):
        if user_input:
            with st.spinner(f"Running GHunt on {task}..."):
                full_command = f"{task_config['command']} {user_input}"
                output = run_ghunt_command(full_command)
                st.text_area("Output:", output, height=300)
        else:
            st.warning(f"Please provide a valid {task.lower()}.")

def render_footer():
    """Render the footer section."""
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

# ----------------- MAIN APP FUNCTION -----------------
def render_ghunt_interface():
    """Main interface for GHunt tool that can be called from homepage."""
    render_header()
    
    # Initialize session state for task selection if not exists
    if 'selected_task' not in st.session_state:
        st.session_state.selected_task = None
    
    # Get selected task from session state or task selector
    selected_task = st.session_state.selected_task or render_task_selector()
    
    if selected_task:
        st.session_state.selected_task = selected_task
        render_task_interface(selected_task)
        
        # Add a back button
        if st.button("← Back to Task Selection", use_container_width=True):
            st.session_state.selected_task = None
            st.rerun()
    
    render_footer()

def main():
    """Standalone entry point for running GHunt directly."""
    render_ghunt_interface()

# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    main()





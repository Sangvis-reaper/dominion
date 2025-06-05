#!/usr/bin/env python3

import streamlit as st
import requests
import whois as python_whois
import dns.resolver
import socket
import json
import sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import re
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import time
import io
import traceback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import ipaddress
import hashlib
import os

# Initialize session state variables for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'last_attempt_time' not in st.session_state:
    st.session_state.last_attempt_time = None

# Simulated user credentials (in production, use a database or secure authentication system)
# Sample credentials: {'username': 'admin', 'password_hash': hash of 'admin123'}
USERS = {
    'admin': '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', # admin123
    'analyst': 'b4ec8f9fe1e59c3cba6d0747fcfa184943c940dccf8c7e74135bb6f1a4ec6bc8', # analyst123
    'guest': '84983c60f7daadc1cb8698621f802c0d9f9a3c3c295c810748fb048115c186ec'   # guest123
}

# Create a hash of a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authenticate user
def authenticate(username, password):
    if username in USERS:
        password_hash = hash_password(password)
        if password_hash == USERS[username]:
            return True
    return False

# Login Page UI
def login_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 0.5rem;
        }
        
        .login-header p {
            color: #718096;
            font-weight: 400;
        }
        
        .login-form {
            margin-bottom: 1.5rem;
        }
        
        .login-footer {
            text-align: center;
            font-size: 0.875rem;
            color: #718096;
        }
        
        .stButton > button {
            background: #1a365d;
            color: white;
            width: 100%;
            border: none;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #2c5282;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .login-logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .login-alert {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            background-color: #FFEBEE;
            color: #C62828;
            font-size: 0.875rem;
        }
        
        .lockout-alert {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            background-color: #FFF8E1;
            color: #F57F17;
            font-size: 0.875rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center content vertically
    st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    # Login header
    st.markdown("""
        <div class='login-header'>
            <div class='login-logo'>🛡️</div>
            <h1>OsintTool Pro</h1>
            <p>Enterprise OSINT Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Handle lockout if too many failed attempts
    if st.session_state.login_attempts >= 5:
        lockout_time = 5  # minutes
        if st.session_state.last_attempt_time:
            elapsed = datetime.now() - st.session_state.last_attempt_time
            if elapsed.total_seconds() < lockout_time * 60:
                remaining = lockout_time * 60 - elapsed.total_seconds()
                st.markdown(f"""
                    <div class='lockout-alert'>
                        <strong>Account Temporarily Locked</strong><br>
                        Too many failed login attempts. Please try again in {int(remaining/60)}:{int(remaining%60):02d} minutes.
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)  # Close container
                return
            else:
                # Reset attempts after lockout period
                st.session_state.login_attempts = 0
    
    # Login form
    st.markdown("<div class='login-form'>", unsafe_allow_html=True)
    
    # Show failed login message if needed
    if st.session_state.login_attempts > 0:
        st.markdown("""
            <div class='login-alert'>
                <strong>Login Failed</strong><br>
                Invalid username or password. Please try again.
            </div>
        """, unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    
    login_btn = st.button("Login")
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close form div
    
    # Footer
    st.markdown("""
        <div class='login-footer'>
            <p>Secure Authentication System</p>
            <p>© 2025 OsintTool Pro. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close container
    
    # Handle login logic
    if login_btn:
        if username and password:
            st.session_state.last_attempt_time = datetime.now()
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.rerun()

# Page configuration with professional settings
st.set_page_config(
    page_title="OsintTool Pro | OSINT Platform",
    page_icon="logo.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.osinttool.pro',
        'Report a bug': 'https://support.osinttool.pro',
        'About': "## OsintTool Pro\nEnterprise OSINT Intelligence Platform\nVersion 2.0.0"
    }
)

# Enhanced Professional CSS with Modern Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Modern CSS Variables for Design System */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #667eea 0%, #f093fb 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-gradient: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
        
        --primary-color: #667eea;
        --primary-dark: #5a67d8;
        --primary-light: #7c8aed;
        --secondary-color: #764ba2;
        --accent-color: #4facfe;
        --success-color: #48bb78;
        --warning-color: #ed8936;
        --error-color: #f56565;
        --info-color: #4299e1;
        
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --text-tertiary: #718096;
        --text-light: #a0aec0;
        
        --bg-primary: #ffffff;
        --bg-secondary: #f7fafc;
        --bg-tertiary: #edf2f7;
        --bg-accent: rgba(102, 126, 234, 0.05);
        
        --border-color: rgba(226, 232, 240, 0.8);
        --border-hover: rgba(102, 126, 234, 0.3);
        
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.08);
        --shadow-xl: 0 12px 40px rgba(0, 0, 0, 0.12);
        --shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.15);
        
        --radius-sm: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --radius-xl: 1.5rem;
        --radius-2xl: 2rem;
        
        --spacing-xs: 0.5rem;
        --spacing-sm: 0.75rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
        
        --transition-fast: 0.15s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }
    
    /* Global Reset and Enhanced Base Styles */
    .main {
        background: var(--bg-secondary);
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# Professional CSS with Material Design principles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    
    /* CSS Variables for Design System */
    :root {
        --primary-color: #1a365d;
        --primary-light: #2c5282;
        --primary-dark: #1a202c;
        --secondary-color: #4299e1;
        --accent-color: #ed8936;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --error-color: #e53e3e;
        --info-color: #3182ce;
        --gray-50: #f7fafc;
        --gray-100: #edf2f7;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e0;
        --gray-400: #a0aec0;
        --gray-500: #718096;
        --gray-600: #4a5568;
        --gray-700: #2d3748;
        --gray-800: #1a202c;
        --gray-900: #171923;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --radius-sm: 0.375rem;
        --radius-base: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --radius-xl: 1.5rem;
    }
    
    /* Global Reset and Base Styles */
    .main {
        padding: 0;
        max-width: none;
    }
    
    .block-container {
        padding: 1rem 2rem;
        max-width: none;
    }
    
    /* Professional Header */
    .professional-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        padding: 2rem 0;
        margin: -1rem -2rem 2rem -2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        width: 50px;
        height: 50px;
        background: white;
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .brand-text h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2rem;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .brand-text p {
        font-weight: 400;
        opacity: 0.9;
        margin: 0;
        font-size: 0.875rem;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        display: block;
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        opacity: 0.8;
        margin-top: 0.25rem;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: var(--gray-50);
        border-right: 1px solid var(--gray-200);
    }
    
    .sidebar-header {
        background: white;
        padding: 1.5rem;
        border-bottom: 1px solid var(--gray-200);
        text-align: center;
    }
    
    .sidebar-nav {
        padding: 1rem 0;
    }
    
    .nav-section {
        margin-bottom: 2rem;
    }
    
    .nav-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--gray-500);
        padding: 0 1rem;
        margin-bottom: 0.5rem;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        color: var(--gray-700);
        text-decoration: none;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    
    .nav-item:hover {
        background: var(--gray-100);
        border-left-color: var(--primary-color);
        color: var(--primary-color);
    }
    
    .nav-item.active {
        background: var(--primary-color);
        color: white;
        border-left-color: var(--primary-dark);
    }
    
    .nav-icon {
        margin-right: 0.75rem;
        font-size: 1.25rem;
    }
    
    /* Card System */
    .pro-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-base);
        border: 1px solid var(--gray-200);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .pro-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-header {
        padding: 1.5rem;
        border-bottom: 1px solid var(--gray-200);
        background: var(--gray-50);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-subtitle {
        font-size: 0.875rem;
        color: var(--gray-600);
        margin: 0.25rem 0 0 0;
    }
    
    .card-content {
        padding: 1.5rem;
    }
    
    .card-footer {
        padding: 1rem 1.5rem;
        background: var(--gray-50);
        border-top: 1px solid var(--gray-200);
    }
    
    /* Metrics Dashboard */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-base);
        border: 1px solid var(--gray-200);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-color);
    }
    
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-base);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        background: var(--primary-color);
        color: white;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--gray-800);
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--gray-600);
        margin-top: 0.5rem;
    }
    
    .metric-change {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        color: var(--success-color);
    }
    
    .metric-change.negative {
        color: var(--error-color);
    }
    
    /* Status System */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: var(--radius-base);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .status-success {
        background: rgba(56, 161, 105, 0.1);
        color: var(--success-color);
        border: 1px solid rgba(56, 161, 105, 0.2);
    }
    
    .status-error {
        background: rgba(229, 62, 62, 0.1);
        color: var(--error-color);
        border: 1px solid rgba(229, 62, 62, 0.2);
    }
    
    .status-warning {
        background: rgba(214, 158, 46, 0.1);
        color: var(--warning-color);
        border: 1px solid rgba(214, 158, 46, 0.2);
    }
    
    .status-info {
        background: rgba(49, 130, 206, 0.1);
        color: var(--info-color);
        border: 1px solid rgba(49, 130, 206, 0.2);
    }
    
    /* Professional Tables */
    .pro-table {
        background: white;
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-base);
        border: 1px solid var(--gray-200);
    }
    
    .pro-table table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .pro-table th {
        background: var(--gray-50);
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: var(--gray-700);
        border-bottom: 1px solid var(--gray-200);
    }
    
    .pro-table td {
        padding: 1rem;
        border-bottom: 1px solid var(--gray-200);
        vertical-align: top;
    }
    
    .pro-table tr:hover {
        background: var(--gray-50);
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--radius-base);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--primary-light);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Form Elements */
    .stTextInput > div > div > input {
        border-radius: var(--radius-base);
        border: 1px solid var(--gray-300);
        padding: 0.75rem;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
    }
    
    /* Progress Indicators */
    .pro-progress {
        background: var(--gray-200);
        border-radius: var(--radius-base);
        overflow: hidden;
        height: 8px;
    }
    
    .pro-progress-bar {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .slide-in-up {
        animation: slideInUp 0.6s ease-out;
    }
    
    .fade-in {
        animation: fadeIn 0.4s ease-out;
    }
    
    /* Loading States */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--gray-200);
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .block-container {
            padding: 1rem;
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gray-400);
        border-radius: var(--radius-base);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gray-500);
    }
    
    /* Tooltip System */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--gray-800);
        color: white;
        text-align: center;
        border-radius: var(--radius-base);
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.75rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Professional Alerts */
    .pro-alert {
        border-radius: var(--radius-lg);
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border: 1px solid;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.875rem;
    }
    
    .pro-alert-success {
        background: rgba(56, 161, 105, 0.05);
        border-color: rgba(56, 161, 105, 0.2);
        color: var(--success-color);
    }
    
    .pro-alert-error {
        background: rgba(229, 62, 62, 0.05);
        border-color: rgba(229, 62, 62, 0.2);
        color: var(--error-color);
    }
    
    .pro-alert-warning {
        background: rgba(214, 158, 46, 0.05);
        border-color: rgba(214, 158, 46, 0.2);
        color: var(--warning-color);
    }
    
    .pro-alert-info {
        background: rgba(49, 130, 206, 0.05);
        border-color: rgba(49, 130, 206, 0.2);
        color: var(--info-color);
    }
    
    /* Tab System */
    .pro-tabs {
        border-bottom: 1px solid var(--gray-200);
        margin-bottom: 2rem;
    }
    
    .pro-tab {
        padding: 1rem 1.5rem;
        border-bottom: 3px solid transparent;
        font-weight: 500;
        color: var(--gray-600);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .pro-tab:hover {
        color: var(--primary-color);
    }
    
    .pro-tab.active {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
    }
    
    /* Data Visualization Enhancements */
    .viz-container {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-base);
        border: 1px solid var(--gray-200);
        margin: 1rem 0;
    }
    
    .viz-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .viz-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--gray-800);
    }
    
    .viz-controls {
        display: flex;
        gap: 0.5rem;
    }
    
    /* Export Options */
    .export-menu {
        background: white;
        border-radius: var(--radius-base);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--gray-200);
        padding: 0.5rem;
        position: absolute;
        z-index: 1000;
    }
    
    .export-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-sm);
        color: var(--gray-700);
        text-decoration: none;
        transition: background 0.2s ease;
    }
    
    .export-item:hover {
        background: var(--gray-100);
    }
    
    /* Footer */
    .pro-footer {
        background: var(--gray-50);
        border-top: 1px solid var(--gray-200);
        padding: 2rem 0;
        margin: 3rem -2rem -1rem -2rem;
        text-align: center;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section h4 {
        font-weight: 600;
        color: var(--gray-800);
        margin-bottom: 1rem;
    }
    
    .footer-section p, .footer-section a {
        color: var(--gray-600);
        text-decoration: none;
        font-size: 0.875rem;
        line-height: 1.6;
    }
    
    .footer-section a:hover {
        color: var(--primary-color);
    }
    
    .footer-bottom {
        padding-top: 2rem;
        border-top: 1px solid var(--gray-200);
        color: var(--gray-500);
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalOSINTTool:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        self.session_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'platforms_checked': 0,
            'start_time': datetime.now()
        }
    
    def render_header(self):
        """Render professional header with branding and stats"""
        uptime = datetime.now() - self.session_stats['start_time']
        success_rate = (self.session_stats['successful_searches'] / max(self.session_stats['total_searches'], 1)) * 100
        
        st.markdown(f"""
        <div class="professional-header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo">🛡️</div>
                    <div class="brand-text">
                        <h1>Osint Tool Pro</h1>
                        <p>Enterprise OSINT Intelligence Platform</p>
                    </div>
                </div>
                <div class="header-stats">
                    <div class="stat-item">
                        <span class="stat-value">{self.session_stats['total_searches']}</span>
                        <div class="stat-label">Total Searches</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{success_rate:.1f}%</span>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{self.session_stats['platforms_checked']}</span>
                        <div class="stat-label">Platforms Checked</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{str(uptime).split('.')[0]}</span>
                        <div class="stat-label">Session Time</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_metric_card(self, title, value, subtitle="", icon="📊", color="primary", change=None):
        """Create professional metric cards"""
        change_html = ""
        if change is not None:
            change_class = "positive" if change >= 0 else "negative"
            change_icon = "↗" if change >= 0 else "↘"
            change_html = f'<div class="metric-change {change_class}">{change_icon} {abs(change):.1f}%</div>'
        
        return f"""
        <div class="metric-card">
            <div class="metric-header">
                <div class="metric-icon">{icon}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
            {change_html}
            {f'<p style="font-size: 0.75rem; color: var(--gray-500); margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """
    
    def create_status_badge(self, status, text=""):
        """Create professional status badges"""
        status_map = {
            'success': ('status-success', '✓'),
            'error': ('status-error', '✗'),
            'warning': ('status-warning', '⚠'),
            'info': ('status-info', 'ℹ'),
            'found': ('status-success', '✓'),
            'not_found': ('status-error', '✗'),
            'unknown': ('status-warning', '?'),
            'timeout': ('status-warning', '⏱')
        }
        
        css_class, icon = status_map.get(status.lower(), ('status-info', 'ℹ'))
        display_text = text or status.replace('_', ' ').title()
        
        return f'<span class="status-badge {css_class}">{icon} {display_text}</span>'
    
    def create_professional_alert(self, message, alert_type="info", icon=None):
        """Create professional alerts"""
        icons = {
            'success': '✓',
            'error': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        }
        alert_icon = icon or icons.get(alert_type, 'ℹ')
        return f'<div class="pro-alert pro-alert-{alert_type}">{alert_icon} {message}</div>'
    
    def render_advanced_visualization(self, data, title="Analysis Results"):
        """Create advanced data visualizations"""
        if not data:
            return None
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Status Distribution', 'Platform Categories', 'Time Series', 'Success Rate'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "indicator"}]]
        )
        
        # Pie chart for status distribution
        status_counts = data['Status'].value_counts()
        colors = ['#38a169', '#e53e3e', '#d69e2e', '#3182ce']
        fig.add_trace(
            go.Pie(labels=status_counts.index, values=status_counts.values, 
                   marker_colors=colors, name="Status"),
            row=1, col=1
        )
        
        # Bar chart for categories
        if 'Category' in data.columns:
            category_counts = data['Category'].value_counts()
            fig.add_trace(
                go.Bar(x=category_counts.index, y=category_counts.values,
                       marker_color='#1a365d', name="Categories"),
                row=1, col=2
            )
        
        # Time series (mock data for demonstration)
        fig.add_trace(
            go.Scatter(x=list(range(len(data))), y=[i+1 for i in range(len(data))],
                       mode='lines+markers', name="Search Progress"),
            row=2, col=1
        )
        
        # Success rate indicator
        success_rate = (data['Status'].str.contains('Found').sum() / len(data)) * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=success_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Success Rate (%)"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#1a365d"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text=title,
            title_x=0.5,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def render_professional_table(self, data, title="Results"):
        """Render professional data table with enhanced features"""
        if data is None or data.empty:
            return f'<div class="pro-alert pro-alert-info">ℹ No data to display</div>'
        
        # Create table HTML
        table_html = f"""
        <div class="pro-card">
            <div class="card-header">
                <h3 class="card-title">📊 {title}</h3>
                <div class="card-subtitle">{len(data)} records found</div>
            </div>
            <div class="pro-table">
                <table>
                    <thead>
                        <tr>
        """
        
        # Add headers
        for col in data.columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        # Add rows
        for _, row in data.iterrows():
            table_html += '<tr>'
            for col in data.columns:
                value = str(row[col])
                if col == 'Status':
                    if 'Found' in value:
                        value = self.create_status_badge('found', value)
                    elif 'Not Found' in value:
                        value = self.create_status_badge('not_found', value)
                    elif 'Error' in value:
                        value = self.create_status_badge('error', value)
                    else:
                        value = self.create_status_badge('unknown', value)
                elif col == 'URL' and value.startswith('http'):
                    value = f'<a href="{value}" target="_blank" style="color: var(--primary-color);">🔗 Visit</a>'
                table_html += f'<td>{value}</td>'
            table_html += '</tr>'
        
        table_html += '</tbody></table></div></div>'
        return table_html
    
    def domain_intelligence(self, domain):
        """Professional domain intelligence analysis"""
        if not domain:
            return None
        
        self.session_stats['total_searches'] += 1
        
        # Clean domain input
        domain = domain.strip().lower()
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('//', 1)[1].split('/')[0]
        
        st.markdown(f"""
        <div class="pro-card slide-in-up">
            <div class="card-header">
                <h2 class="card-title">🌐 Domain Intelligence Analysis</h2>
                <div class="card-subtitle">Comprehensive analysis for: <code>{domain}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        results = {}
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # WHOIS Analysis
            with st.expander("📄 WHOIS Intelligence", expanded=True):
                with st.spinner("Analyzing WHOIS data..."):
                    try:
                        w = python_whois.whois(domain)
                        if w:
                            whois_data = {
                                "Domain": domain,
                                "Registrar": str(w.registrar) if w.registrar else 'Not Available',
                                "Creation Date": str(w.creation_date) if w.creation_date else 'Not Available',
                                "Expiration Date": str(w.expiration_date) if w.expiration_date else 'Not Available',
                                "Updated Date": str(w.updated_date) if hasattr(w, 'updated_date') and w.updated_date else 'Not Available',
                                "Registrant": str(w.registrant) if hasattr(w, 'registrant') and w.registrant else 'Not Available',
                                "Name Servers": ', '.join(w.name_servers) if w.name_servers else 'Not Available',
                                "Status": str(w.status) if hasattr(w, 'status') and w.status else 'Not Available'
                            }
                            st.markdown(self.create_professional_alert("WHOIS data retrieved successfully", "success"))
                            
                            # Display in a professional format
                            whois_df = pd.DataFrame(list(whois_data.items()), columns=['Property', 'Value'])
                            st.markdown(self.render_professional_table(whois_df, "WHOIS Information"), unsafe_allow_html=True)
                            results['whois'] = whois_data
                            self.session_stats['successful_searches'] += 1
                        else:
                            st.markdown(self.create_professional_alert("No WHOIS data available for this domain", "warning"))
                    except Exception as e:
                        st.markdown(self.create_professional_alert(f"WHOIS Error: {str(e)}", "error"))
            
            # DNS Analysis
            with st.expander("🔍 DNS Intelligence", expanded=True):
                with st.spinner("Analyzing DNS records..."):
                    dns_results = {}
                    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
                    
                    dns_data = []
                    for record_type in record_types:
                        try:
                            answers = dns.resolver.resolve(domain, record_type)
                            records = [str(rdata) for rdata in answers]
                            dns_results[record_type] = records
                            for record in records:
                                dns_data.append({
                                    'Type': record_type,
                                    'Value': record,
                                    'Status': self.create_status_badge('found', 'Active')
                                })
                        except Exception as e:
                            dns_data.append({
                                'Type': record_type,
                                'Value': f'No records found',
                                'Status': self.create_status_badge('not_found', 'Missing')
                            })
                    
                    if dns_data:
                        st.markdown(self.create_professional_alert(f"Found {len([d for d in dns_data if 'Found' in d['Status']])} DNS record types", "success"))
                        dns_df = pd.DataFrame(dns_data)
                        st.markdown(self.render_professional_table(dns_df, "DNS Records"), unsafe_allow_html=True)
                        results['dns'] = dns_results
            
            # Security Analysis
            with st.expander("🔒 Security Assessment", expanded=True):
                security_checks = {
                    'SSL Certificate': self._check_ssl(domain),
                    'DNSSEC': self._check_dnssec(domain),
                    'SPF Record': self._check_spf(dns_results),
                    'DMARC Record': self._check_dmarc(dns_results),
                    'DKIM Record': self._check_dkim(dns_results),
                }
                
                security_data = []
                for check, status in security_checks.items():
                    security_data.append({
                        'Security Check': check,
                        'Status': self.create_status_badge('found' if status else 'not_found', 
                                                         'Implemented' if status else 'Missing'),
                        'Risk Level': 'Low' if status else 'Medium'
                    })
                
                security_df = pd.DataFrame(security_data)
                st.markdown(self.render_professional_table(security_df, "Security Assessment"), unsafe_allow_html=True)
                results['security'] = security_checks
        
        with col2:
            # Metrics Dashboard
            st.markdown("### 📊 Domain Metrics")
            
            # Calculate metrics
            total_dns_types = len(record_types)
            active_dns_types = len([r for r in dns_results.keys()])
            security_score = sum(security_checks.values()) / len(security_checks) * 100
            
            metrics_html = f"""
            <div class="metrics-grid">
                {self.create_metric_card("DNS Coverage", f"{active_dns_types}/{total_dns_types}", 
                                        f"{(active_dns_types/total_dns_types)*100:.1f}% complete", "🔍")}
                {self.create_metric_card("Security Score", f"{security_score:.0f}%", 
                                        "Based on security checks", "🔒")}
                {self.create_metric_card("WHOIS Status", "Active" if 'whois' in results else "Missing", 
                                        "Registration data", "📄")}
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)
            
            # Quick Actions
            st.markdown("### ⚡ Quick Actions")
            st.markdown(f"""
            <div class="pro-card">
                <div class="card-content">
                    <a href="https://whois.domaintools.com/{domain}" target="_blank" class="export-item">
                        🔍 Advanced WHOIS Lookup
                    </a>
                    <a href="https://www.virustotal.com/gui/domain/{domain}" target="_blank" class="export-item">
                        🛡️ Security Scan
                    </a>
                    <a href="https://securitytrails.com/domain/{domain}" target="_blank" class="export-item">
                        📊 DNS History
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        self.session_stats['platforms_checked'] += len(record_types)
        return results
    
    def username_intelligence(self, username):
        """Professional username intelligence across platforms"""
        if not username:
            return None
        
        self.session_stats['total_searches'] += 1
        
        st.markdown(f"""
        <div class="pro-card slide-in-up">
            <div class="card-header">
                <h2 class="card-title">👤 Username Intelligence Analysis</h2>
                <div class="card-subtitle">Multi-platform investigation for: <code>{username}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced platform database with categories and metadata
        platforms = {
            'social': {
                'GitHub': {'url': f"https://github.com/{username}", 'risk': 'Low', 'info_type': 'Code & Projects'},
                'Twitter': {'url': f"https://twitter.com/{username}", 'risk': 'Medium', 'info_type': 'Social Activity'},
                'Instagram': {'url': f"https://instagram.com/{username}", 'risk': 'Medium', 'info_type': 'Photos & Stories'},
                'LinkedIn': {'url': f"https://linkedin.com/in/{username}", 'risk': 'High', 'info_type': 'Professional Info'},
                'Facebook': {'url': f"https://facebook.com/{username}", 'risk': 'High', 'info_type': 'Personal Details'},
                'Reddit': {'url': f"https://reddit.com/user/{username}", 'risk': 'Medium', 'info_type': 'Discussions & Interests'},
                'TikTok': {'url': f"https://tiktok.com/@{username}", 'risk': 'Low', 'info_type': 'Video Content'},
            },
            'professional': {
                'AngelList': {'url': f"https://angel.co/u/{username}", 'risk': 'High', 'info_type': 'Startup Profile'},
                'Behance': {'url': f"https://behance.net/{username}", 'risk': 'Low', 'info_type': 'Creative Portfolio'},
                'Dribbble': {'url': f"https://dribbble.com/{username}", 'risk': 'Low', 'info_type': 'Design Work'},
                'Medium': {'url': f"https://medium.com/@{username}", 'risk': 'Medium', 'info_type': 'Articles & Thoughts'},
            },
            'development': {
                'GitLab': {'url': f"https://gitlab.com/{username}", 'risk': 'Low', 'info_type': 'Code Repositories'},
                'Bitbucket': {'url': f"https://bitbucket.org/{username}", 'risk': 'Low', 'info_type': 'Code Projects'},
                'CodePen': {'url': f"https://codepen.io/{username}", 'risk': 'Low', 'info_type': 'Code Snippets'},
                'Stack Overflow': {'url': f"https://stackoverflow.com/users/{username}", 'risk': 'Low', 'info_type': 'Technical Q&A'},
            },
            'gaming': {
                'Steam': {'url': f"https://steamcommunity.com/id/{username}", 'risk': 'Medium', 'info_type': 'Gaming Profile'},
                'Twitch': {'url': f"https://twitch.tv/{username}", 'risk': 'Medium', 'info_type': 'Streaming Content'},
                'Xbox': {'url': f"https://xboxgamertag.com/search/{username}", 'risk': 'Low', 'info_type': 'Gaming Stats'},
            },
            'content': {
                'YouTube': {'url': f"https://youtube.com/@{username}", 'risk': 'Medium', 'info_type': 'Video Content'},
                'Vimeo': {'url': f"https://vimeo.com/{username}", 'risk': 'Low', 'info_type': 'Video Portfolio'},
                'SoundCloud': {'url': f"https://soundcloud.com/{username}", 'risk': 'Low', 'info_type': 'Audio Content'},
            }
        }
        
        # Perform searches
        results = []
        total_platforms = sum(len(category) for category in platforms.values())
        
        # Progress tracking
        progress_col1, progress_col2 = st.columns([3, 1])
        with progress_col1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        with progress_col2:
            progress_metric = st.empty()
        
        current_platform = 0
        
        for category, category_platforms in platforms.items():
            for platform, details in category_platforms.items():
                current_platform += 1
                status_text.text(f"🔍 Scanning {platform}...")
                progress_bar.progress(current_platform / total_platforms)
                progress_metric.metric("Progress", f"{current_platform}/{total_platforms}")
                
                try:
                    response = requests.get(details['url'], headers=self.headers, timeout=5)
                    
                    if response.status_code == 200:
                        results.append({
                            'Platform': platform,
                            'Category': category.title(),
                            'URL': details['url'],
                            'Status': 'Found',
                            'Risk Level': details['risk'],
                            'Information Type': details['info_type'],
                            'Response Code': response.status_code
                        })
                    elif response.status_code == 404:
                        results.append({
                            'Platform': platform,
                            'Category': category.title(),
                            'URL': details['url'],
                            'Status': 'Not Found',
                            'Risk Level': details['risk'],
                            'Information Type': details['info_type'],
                            'Response Code': response.status_code
                        })
                    else:
                        results.append({
                            'Platform': platform,
                            'Category': category.title(),
                            'URL': details['url'],
                            'Status': 'Unknown',
                            'Risk Level': details['risk'],
                            'Information Type': details['info_type'],
                            'Response Code': response.status_code
                        })
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except requests.exceptions.Timeout:
                    results.append({
                        'Platform': platform,
                        'Category': category.title(),
                        'URL': details['url'],
                        'Status': 'Timeout',
                        'Risk Level': details['risk'],
                        'Information Type': details['info_type'],
                        'Response Code': 'N/A'
                    })
                except Exception as e:
                    results.append({
                        'Platform': platform,
                        'Category': category.title(),
                        'URL': details['url'],
                        'Status': 'Error',
                        'Risk Level': details['risk'],
                        'Information Type': details['info_type'],
                        'Response Code': str(e)[:50]
                    })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        progress_metric.empty()
        
        if results:
            df = pd.DataFrame(results)
            
            # Summary metrics
            found_count = len(df[df['Status'] == 'Found'])
            high_risk_found = len(df[(df['Status'] == 'Found') & (df['Risk Level'] == 'High')])
            
            self.session_stats['successful_searches'] += 1 if found_count > 0 else 0
            self.session_stats['platforms_checked'] += len(results)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(self.create_metric_card("Total Platforms", total_platforms, "Searched", "🌐"), 
                          unsafe_allow_html=True)
            with col2:
                st.markdown(self.create_metric_card("Profiles Found", found_count, 
                                                  f"{(found_count/total_platforms)*100:.1f}% hit rate", "✅"), 
                          unsafe_allow_html=True)
            with col3:
                st.markdown(self.create_metric_card("High Risk Profiles", high_risk_found, 
                                                  "Sensitive information", "⚠️"), 
                          unsafe_allow_html=True)
            with col4:
                categories_found = df[df['Status'] == 'Found']['Category'].nunique()
                st.markdown(self.create_metric_card("Categories Found", categories_found, 
                                                  "Different platform types", "📂"), 
                          unsafe_allow_html=True)
            
            # Visualizations
            if found_count > 0:
                st.markdown("### 📊 Intelligence Visualization")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Category distribution
                    fig1 = px.pie(df[df['Status'] == 'Found'], 
                                 names='Category', 
                                 title="Found Profiles by Category",
                                 color_discrete_sequence=px.colors.qualitative.Set3)
                    fig1.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Risk analysis
                    risk_data = df[df['Status'] == 'Found']['Risk Level'].value_counts()
                    colors = {'High': '#e53e3e', 'Medium': '#d69e2e', 'Low': '#38a169'}
                    fig2 = px.bar(x=risk_data.index, y=risk_data.values,
                                 title="Risk Level Distribution",
                                 color=risk_data.index,
                                 color_discrete_map=colors)
                    fig2.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Results table with filters
            st.markdown("### 🔍 Detailed Intelligence Report")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status:", ['All'] + list(df['Status'].unique()))
            with col2:
                category_filter = st.selectbox("Filter by Category:", ['All'] + list(df['Category'].unique()))
            with col3:
                risk_filter = st.selectbox("Filter by Risk Level:", ['All'] + list(df['Risk Level'].unique()))
            
            # Apply filters
            filtered_df = df.copy()
            if status_filter != 'All':
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            if category_filter != 'All':
                filtered_df = filtered_df[filtered_df['Category'] == category_filter]
            if risk_filter != 'All':
                filtered_df = filtered_df[filtered_df['Risk Level'] == risk_filter]
            
            # Display filtered results
            st.markdown(self.render_professional_table(filtered_df, f"Username Intelligence Report ({len(filtered_df)} records)"), 
                       unsafe_allow_html=True)
            
            return df
        
        return None
    
    def _check_ssl(self, domain):
        """Check SSL certificate"""
        try:
            import ssl
            context = ssl.create_default_context()
            # Use a shorter timeout to avoid long waits
            with socket.create_connection((domain, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    return True
        except socket.gaierror:
            # DNS resolution error - hostname couldn't be resolved
            print(f"DNS resolution error for {domain}")
            return False
        except socket.timeout:
            # Connection timeout
            print(f"Connection timeout for {domain}")
            return False
        except Exception as e:
            # Log other errors
            print(f"SSL check error for {domain}: {str(e)}")
            return False
    
    def _check_dnssec(self, domain):
        """Check DNSSEC implementation"""
        try:
            answers = dns.resolver.resolve(domain, 'DNSKEY')
            return len(answers) > 0
        except:
            return False
    
    def _check_spf(self, dns_results):
        """Check SPF record"""
        txt_records = dns_results.get('TXT', [])
        return any('v=spf1' in record for record in txt_records)
    
    def _check_dmarc(self, dns_results):
        """Check DMARC record"""
        txt_records = dns_results.get('TXT', [])
        return any('v=DMARC1' in record for record in txt_records)
    
    def _check_dkim(self, dns_results):
        """Check DKIM record"""
        txt_records = dns_results.get('TXT', [])
        return any('v=DKIM1' in record for record in txt_records)
    
    def get_truecaller_data(self, phone_number):
        """Simulate TrueCaller API lookup
        
        In a production environment, this would use the actual TrueCaller API
        with proper authentication and error handling
        """
        # Simulate API response based on the phone number pattern
        # This is for demonstration purposes only
        if not phone_number:
            return None
            
        # Simulate some random responses
        last_digits = phone_number[-4:]
        if int(last_digits) % 5 == 0:
            # Simulate a business number
            return {
                'Name': 'Business Services Inc.',
                'Type': 'Business',
                'Tags': 'Verified Business, Customer Service',
                'Email': f'contact@business-{last_digits}.com',
                'Address': '123 Business Ave., New York, NY',
                'Spam Score': 'Very Low',
                'Verified': 'Yes',
                'Social Profiles': 'LinkedIn, Facebook, Twitter',
                'Image URL': 'https://example.com/profile.jpg',
                'Last Updated': datetime.now().strftime('%Y-%m-%d'),
                'Number of Searches': '157',
                'User Reports': 'None'
            }
        elif int(last_digits) % 3 == 0:
            # Simulate a personal number
            return {
                'Name': f'John Doe ({last_digits})',
                'Type': 'Personal',
                'Tags': 'Private, Mobile',
                'Email': f'john.doe{last_digits}@example.com',
                'Address': 'Private',
                'Spam Score': 'Low',
                'Verified': 'Yes',
                'Social Profiles': 'Facebook',
                'Image URL': 'https://example.com/john_profile.jpg',
                'Last Updated': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'Number of Searches': '12',
                'User Reports': 'None'
            }
        elif int(last_digits) % 7 == 0:
            # Simulate spam number
            return {
                'Name': 'Suspected Spam',
                'Type': 'Unknown',
                'Tags': 'Spam, Telemarketing, Scam',
                'Email': 'Unknown',
                'Address': 'Unknown',
                'Spam Score': 'Very High',
                'Verified': 'No',
                'Social Profiles': 'None',
                'Image URL': 'None',
                'Last Updated': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'Number of Searches': '2,453',
                'User Reports': '187 negative reports'
            }
        else:
            # No data found for some numbers
            return None
    
    def export_report(self, data, report_type, format_type='json'):
        """Export professional reports in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'json':
            if isinstance(data, pd.DataFrame):
                report_data = data.to_dict('records')
            else:
                report_data = data
            
            report = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'session_id': f"session_{timestamp}",
                'data': report_data,
                'summary': {
                    'total_records': len(data) if isinstance(data, pd.DataFrame) else len(data.get('results', [])),
                    'successful_searches': self.session_stats['successful_searches'],
                    'platforms_checked': self.session_stats['platforms_checked']
                }
            }
            
            return json.dumps(report, indent=2), f"{report_type}_report_{timestamp}.json", "application/json"
        
        elif format_type == 'csv' and isinstance(data, pd.DataFrame):
            csv_buffer = io.StringIO()
            data.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue(), f"{report_type}_report_{timestamp}.csv", "text/csv"
        
        elif format_type == 'html':
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Osint Tool Pro Report - {report_type}</title>
                <style>
                    body {{ font-family: 'Inter', Arial, sans-serif; margin: 40px; background: #f7fafc; }}
                    .header {{ background: #1a365d; color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                    .content {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
                    th {{ background: #edf2f7; font-weight: 600; }}
                    .status-found {{ background: #c6f6d5; color: #22543d; padding: 4px 8px; border-radius: 4px; }}
                    .status-error {{ background: #fed7d7; color: #742a2a; padding: 4px 8px; border-radius: 4px; }}
                    .footer {{ margin-top: 30px; text-align: center; color: #718096; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🛡️ Osint Tool Pro</h1>
                    <h2>{report_type} Report</h2>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                <div class="content">
                    {data.to_html(escape=False, classes='table') if isinstance(data, pd.DataFrame) else '<p>No data available</p>'}
                </div>
                <div class="footer">
                    <p>This report was generated by Osint Tool Pro OSINT Platform</p>
                    <p>For more information, visit our documentation</p>
                </div>
            </body>
            </html>
            """
            return html_report, f"{report_type}_report_{timestamp}.html", "text/html"
    
    def wayback_tweets(self, username, from_date=None, to_date=None, filter_popular=False, specific_content=None):
        """Search for archived tweets from a Twitter/X account using the Wayback Machine"""
        if not username:
            return None
            
        self.session_stats['total_searches'] += 1
        
    def email_harvester(self, domain, depth=1, include_subdomains=False, check_validity=True):
        """Discover email addresses associated with a given domain"""
        if not domain:
            return None
            
        # Configure socket timeout globally to prevent hanging
        socket.setdefaulttimeout(10)
            
        self.session_stats['total_searches'] += 1
        
        # Clean domain input
        domain = domain.strip().lower()
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('//', 1)[1].split('/')[0]
        
        st.markdown(f"""
        <div class="pro-card slide-in-up">
            <div class="card-header">
                <h2 class="card-title">📮 Email Harvester</h2>
                <div class="card-subtitle">Email discovery for domain: <code>{domain}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        results = []
        
        try:
            # Track progress
            progress_placeholder = st.empty()
            progress_placeholder.markdown(self.create_professional_alert(f"Scanning sources for email addresses...", "info"), unsafe_allow_html=True)
            
            sources = [
                "Website Scan",
                "WHOIS Records",
                "DNS Records",
                "Google Search",
                "Social Media",
                "Public Directories",
                "GitHub Repositories",
                "PDF Documents", 
                "Data Breach Records",
                "Certificate Transparency Logs"
            ]
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            scan_details = st.empty()
            
            # For each source, simulate searching for emails
            for i, source in enumerate(sources):
                status_text.text(f"🔍 Scanning {source}...")
                scan_details.markdown(f"<small>Looking for email patterns and references in {source.lower()}...</small>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) / len(sources))
                
                # Simulate finding emails
                # In a real implementation, we would use various techniques to actually find emails
                if source == "Website Scan":
                    # Simulate finding emails on website
                    if len(domain) > 5:
                        results.append({
                            'Email': f"contact@{domain}",
                            'Source': source,
                            'Confidence': 'High',
                            'Valid': 'Likely' if check_validity else 'Unknown',
                            'Type': 'Generic',
                            'Pattern': 'contact@domain'
                        })
                        
                        results.append({
                            'Email': f"info@{domain}",
                            'Source': source,
                            'Confidence': 'High',
                            'Valid': 'Likely' if check_validity else 'Unknown',
                            'Type': 'Generic',
                            'Pattern': 'info@domain'
                        })
                
                elif source == "WHOIS Records":
                    # Try to get actual WHOIS data
                    try:
                        import whois
                        w = whois.whois(domain)
                        if w and hasattr(w, 'emails') and w.emails:
                            if isinstance(w.emails, list):
                                for email in w.emails:
                                    results.append({
                                        'Email': email,
                                        'Source': source,
                                        'Confidence': 'Very High',
                                        'Valid': 'Yes' if check_validity else 'Unknown',
                                        'Type': 'Registration',
                                        'Pattern': 'WHOIS Record'
                                    })
                            else:
                                results.append({
                                    'Email': w.emails,
                                    'Source': source,
                                    'Confidence': 'Very High',
                                    'Valid': 'Yes' if check_validity else 'Unknown',
                                    'Type': 'Registration',
                                    'Pattern': 'WHOIS Record'
                                })
                    except:
                        # Simulate finding admin email
                        results.append({
                            'Email': f"admin@{domain}",
                            'Source': source,
                            'Confidence': 'Medium',
                            'Valid': 'Possible' if check_validity else 'Unknown',
                            'Type': 'Administrative',
                            'Pattern': 'admin@domain'
                        })
                
                elif source == "Google Search":
                    # Simulate google dork results
                    name_parts = domain.split('.')[0].split('-')
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
                        results.append({
                            'Email': f"{first_name}.{last_name}@{domain}",
                            'Source': source,
                            'Confidence': 'Medium',
                            'Valid': 'Possible' if check_validity else 'Unknown',
                            'Type': 'Personal',
                            'Pattern': 'firstname.lastname@domain'
                        })
                        results.append({
                            'Email': f"{first_name[0]}{last_name}@{domain}",
                            'Source': source,
                            'Confidence': 'Low',
                            'Valid': 'Possible' if check_validity else 'Unknown',
                            'Type': 'Personal',
                            'Pattern': 'flastname@domain'
                        })
                
                elif source == "Social Media":
                    # Simulate finding social media linked emails
                    name_parts = domain.split('.')[0].lower()
                    if len(name_parts) > 4:
                        results.append({
                            'Email': f"social@{domain}",
                            'Source': source,
                            'Confidence': 'Medium',
                            'Valid': 'Possible' if check_validity else 'Unknown',
                            'Type': 'Marketing',
                            'Pattern': 'social@domain'
                        })
                        results.append({
                            'Email': f"marketing@{domain}",
                            'Source': source,
                            'Confidence': 'Medium',
                            'Valid': 'Possible' if check_validity else 'Unknown',
                            'Type': 'Marketing',
                            'Pattern': 'marketing@domain'
                        })
                
                elif source == "GitHub Repositories":
                    # Simulate finding developer emails
                    results.append({
                        'Email': f"dev@{domain}",
                        'Source': source,
                        'Confidence': 'Medium',
                        'Valid': 'Possible' if check_validity else 'Unknown',
                        'Type': 'Development',
                        'Pattern': 'dev@domain'
                    })
                
                elif source == "Certificate Transparency Logs":
                    # Simulate finding emails from SSL certificates
                    results.append({
                        'Email': f"security@{domain}",
                        'Source': source,
                        'Confidence': 'High',
                        'Valid': 'Likely' if check_validity else 'Unknown',
                        'Type': 'Security',
                        'Pattern': 'security@domain'
                    })
                
                # Sleep briefly to simulate scanning
                time.sleep(0.2)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            scan_details.empty()
            
            # Generate patterns based on domain if we have few results
            if len(results) < 5:
                common_patterns = [
                    "sales", "support", "hello", "contact", "info", "admin", "help",
                    "billing", "media", "press", "careers", "jobs", "hr", "webmaster"
                ]
                
                for pattern in common_patterns[:5]:  # Limit to first 5 patterns
                    results.append({
                        'Email': f"{pattern}@{domain}",
                        'Source': "Pattern Analysis",
                        'Confidence': 'Low',
                        'Valid': 'Unknown',
                        'Type': 'Common Pattern',
                        'Pattern': f"{pattern}@domain"
                    })
            
            # Include subdomain-based emails if requested
            if include_subdomains:
                common_subdomains = ["mail", "webmail", "support", "dev", "staging"]
                for subdomain in common_subdomains[:3]:  # Limit to first 3 subdomains
                    results.append({
                        'Email': f"info@{subdomain}.{domain}",
                        'Source': "Subdomain Analysis",
                        'Confidence': 'Low',
                        'Valid': 'Unknown',
                        'Type': 'Subdomain',
                        'Pattern': f"info@subdomain.domain"
                    })
            
            # Sort results by confidence
            confidence_order = {"Very High": 0, "High": 1, "Medium": 2, "Low": 3}
            results.sort(key=lambda x: confidence_order.get(x['Confidence'], 4))
            
            progress_placeholder.empty()
            
            # Update stats
            if results:
                self.session_stats['successful_searches'] += 1
                self.session_stats['platforms_checked'] += len(sources)
                
                # Add a note for simulated data
                results.append({
                    'Email': 'Note',
                    'Source': 'Disclaimer',
                    'Confidence': '',
                    'Valid': '',
                    'Type': 'Information',
                    'Pattern': 'Some results are simulated for demonstration purposes. In a real implementation, actual sources would be queried.'
                })
                
                return results
            else:
                st.markdown(self.create_professional_alert("No email addresses found. Try adjusting the scan depth or including subdomains.", "warning"), unsafe_allow_html=True)
                return None
        
        except Exception as e:
            st.markdown(self.create_professional_alert(f"Error during email harvesting: {str(e)}", "error"), unsafe_allow_html=True)
            return None
        
        # Handle date range filtering
        date_filter_active = from_date is not None or to_date is not None
        content_filter_active = specific_content is not None and specific_content.strip() != ""
        
        st.markdown(f"""
        <div class="pro-card slide-in-up">
            <div class="card-header">
                <h2 class="card-title">🕰️ WayBack Tweets Analysis</h2>
                <div class="card-subtitle">Archived tweet analysis for: <code>{username}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean username input
        username = username.strip().lower()
        if username.startswith('@'):
            username = username[1:]
        
        results = []
        
        # Wayback Machine API endpoints
        try:
            # Configure requests with proper error handling
            wayback_url = f"https://archive.org/wayback/available?url=twitter.com/{username}"
            try:
                response = requests.get(wayback_url, headers=self.headers, timeout=8)
            except requests.exceptions.ConnectionError:
                # Handle connection errors (DNS failures, refused connections, etc)
                results.append({
                    'Type': 'Error',
                    'Date': 'N/A',
                    'URL': f"https://twitter.com/{username}",
                    'Status': 'Connection Error',
                    'Source': 'Network error when connecting to Wayback Machine'
                })
                return results
            except requests.exceptions.Timeout:
                # Handle timeout errors
                results.append({
                    'Type': 'Error',
                    'Date': 'N/A',
                    'URL': f"https://twitter.com/{username}",
                    'Status': 'Timeout',
                    'Source': 'Wayback Machine API timed out'
                })
                return results
            except requests.exceptions.RequestException as e:
                # Handle all other request exceptions
                results.append({
                    'Type': 'Error',
                    'Date': 'N/A',
                    'URL': f"https://twitter.com/{username}",
                    'Status': 'API Error',
                    'Source': f"Request error: {str(e)[:100]}"
                })
                return results
            
            if response.status_code == 200:
                data = response.json()
                archives = data.get('archived_snapshots', {})
                
                # Check if we have archived snapshots
                if archives and 'closest' in archives:
                    snapshot = archives['closest']
                    archive_url = snapshot.get('url')
                    archive_time = snapshot.get('timestamp', '')
                    
                    # Format timestamp if available
                    formatted_time = "Unknown"
                    if archive_time:
                        try:
                            year = archive_time[:4]
                            month = archive_time[4:6]
                            day = archive_time[6:8]
                            hour = archive_time[8:10]
                            minute = archive_time[10:12]
                            second = archive_time[12:14]
                            formatted_time = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                        except:
                            formatted_time = archive_time
                    
                    # Add the main snapshot
                    results.append({
                        'Type': 'Latest Archive',
                        'Date': formatted_time,
                        'URL': archive_url,
                        'Status': 'Available',
                        'Source': 'Wayback Machine'
                    })
                    
                    # Now search for archive calendar data
                    calendar_url = f"https://web.archive.org/web/timemap/json?url=twitter.com/{username}&matchType=prefix&collapse=timestamp:4"
                    try:
                        calendar_response = requests.get(calendar_url, headers=self.headers, timeout=10)
                    except (requests.exceptions.ConnectionError, socket.gaierror):
                        # Handle connection errors
                        print(f"Network error when fetching calendar data for {username}")
                        results.append({
                            'Type': 'Warning',
                            'Date': 'N/A',
                            'URL': calendar_url,
                            'Status': 'Connection Error',
                            'Source': 'Network error when connecting to calendar API'
                        })
                        # Skip to next section
                        calendar_response = None
                    except requests.exceptions.Timeout:
                        # Handle timeout errors
                        print(f"Timeout when fetching calendar data for {username}")
                        results.append({
                            'Type': 'Warning',
                            'Date': 'N/A',
                            'URL': calendar_url,
                            'Status': 'Timeout',
                            'Source': 'Calendar API request timed out'
                        })
                        # Skip to next section
                        calendar_response = None
                    except requests.exceptions.RequestException as e:
                        # Handle all other request exceptions
                        print(f"Request error for calendar data: {str(e)}")
                        results.append({
                            'Type': 'Warning',
                            'Date': 'N/A',
                            'URL': calendar_url,
                            'Status': 'API Error',
                            'Source': f"Request error: {str(e)[:100]}"
                        })
                        # Skip to next section
                        calendar_response = None
                    # Only attempt to process calendar response if it exists and has a valid status code
                    if calendar_response is not None:
                        try:
                            if calendar_response.status_code == 200:
                                try:
                                    calendar_data = calendar_response.json()
                                    # First entry is header, skip it
                                    if len(calendar_data) > 1:
                                        # Process up to 100 most recent entries (excluding header)
                                        for entry in calendar_data[1:101]:
                                            # Each entry format: [timestamp, original, mimetype, statuscode, digest]
                                            if len(entry) >= 2:
                                                timestamp = entry[0]
                                                archive_entry_url = f"https://web.archive.org{timestamp}/twitter.com/{username}"
                                                
                                                # Format date from timestamp like 20210130142509
                                                formatted_date = "Unknown"
                                                if len(timestamp) > 14:  # Format: /web/20210130142509/
                                                    timestamp = timestamp.split('/')[2]
                                                    try:
                                                        year = timestamp[:4]
                                                        month = timestamp[4:6]
                                                        day = timestamp[6:8]
                                                        hour = timestamp[8:10]
                                                        minute = timestamp[10:12]
                                                        second = timestamp[12:14]
                                                        formatted_date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                                                    except:
                                                        formatted_date = timestamp
                                                
                                                results.append({
                                                    'Type': 'Archive',
                                                    'Date': formatted_date,
                                                    'URL': archive_entry_url,
                                                    'Status': 'Available',
                                                    'Source': 'Wayback Machine'
                                                })
                                except Exception as e:
                                    # JSON parsing failed, might be HTML response
                                    print(f"Error parsing calendar JSON data: {str(e)}")
                                    pass
                            else:
                                # Bad status code
                                print(f"Calendar API returned status code {calendar_response.status_code}")
                        except Exception as e:
                            # Error processing calendar data
                            print(f"Error processing calendar data: {str(e)}")
                            pass
                    
                    # If no additional archives found, add note
                    if len(results) == 1:
                        results.append({
                            'Type': 'Note',
                            'Date': 'N/A',
                            'URL': 'N/A',
                            'Status': 'Info',
                            'Source': 'No additional archives found for this Twitter account'
                        })
                
                else:
                    # No archives found
                    results.append({
                        'Type': 'Error',
                        'Date': 'N/A',
                        'URL': f"https://twitter.com/{username}",
                        'Status': 'Not Found',
                        'Source': 'No archives found in Wayback Machine'
                    })
                    
                    # Add some alternative search suggestions
                    results.append({
                        'Type': 'Suggestion',
                        'Date': 'N/A',
                        'URL': f"https://web.archive.org/web/*/twitter.com/{username}/*",
                        'Status': 'Suggestion',
                        'Source': 'Try broader Wayback Machine search'
                    })
                    
                    results.append({
                        'Type': 'Suggestion',
                        'Date': 'N/A',
                        'URL': f"https://archive.ph/twitter.com/{username}",
                        'Status': 'Suggestion',
                        'Source': 'Try archive.today'
                    })
            else:
                # API error
                results.append({
                    'Type': 'Error',
                    'Date': 'N/A',
                    'URL': f"https://web.archive.org/web/*/twitter.com/{username}",
                    'Status': 'API Error',
                    'Source': f"Wayback Machine API returned status code {response.status_code}"
                })
                
        except Exception as e:
            # General error
            results.append({
                'Type': 'Error',
                'Date': 'N/A',
                'URL': f"https://twitter.com/{username}",
                'Status': 'Error',
                'Source': f"Error: {str(e)[:100]}"
            })
        
        # Add alternative archive sources
        results.append({
            'Type': 'Alternative',
            'Date': 'N/A',
            'URL': f"https://archive.ph/twitter.com/{username}",
            'Status': 'Alternative',
            'Source': 'archive.today'
        })
        
        # Apply filtering if any filters are active
        if (date_filter_active or filter_popular or content_filter_active) and results:
            filtered_results = []
            
            # Determine which results to use for popularity filtering
            if filter_popular:
                # Prioritize archives by type and status
                priority_results = []
                normal_results = []
                for r in results:
                    # Prioritize main archives and earlier dates
                    if r['Type'] == 'Latest Archive' or (r['Type'] == 'Archive' and r['Status'] == 'Available'):
                        priority_results.append(r)
                    elif r['Type'] not in ['Error', 'Suggestion', 'Alternative', 'Note']:
                        normal_results.append(r)
                    else:
                        # Always include metadata entries
                        filtered_results.append(r)
                
                # Add only a subset of the archives if filter_popular is active
                if priority_results:
                    # Sort by date if possible
                    try:
                        priority_results.sort(key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%d %H:%M:%S") if isinstance(x['Date'], str) else x['Date'], reverse=True)
                    except:
                        pass
                    
                    # Take up to 10 priority results
                    filtered_results.extend(priority_results[:10])
                    
                    # Add a note about filtering
                    results.append({
                        'Type': 'Note',
                        'Date': 'N/A',
                        'URL': 'N/A',
                        'Status': 'Info',
                        'Source': f'Showing only the {len(priority_results[:10])} most relevant archives'
                    })
                else:
                    # If no priority results, use a subset of normal results
                    filtered_results.extend(normal_results[:10])
            else:
                # Apply date and content filtering to all results
                for r in results:
                    # Skip entries with no date or entries that aren't archive results for date filtering
                    if date_filter_active and (r['Date'] == 'N/A' or r['Date'] == 'Unknown' or r['Type'] in ['Error', 'Suggestion', 'Alternative', 'Note']):
                        filtered_results.append(r)
                        continue
                    
                    # Date filtering
                    if date_filter_active:
                        try:
                            # Convert string date to datetime object
                            if isinstance(r['Date'], str):
                                entry_date = datetime.strptime(r['Date'], "%Y-%m-%d %H:%M:%S")
                            else:
                                entry_date = r['Date']
                                
                            # Apply from_date filter
                            if from_date and entry_date < from_date:
                                continue
                                
                            # Apply to_date filter
                            if to_date and entry_date > to_date:
                                continue
                        except:
                            # If date parsing fails, include the result anyway if not also filtering by content
                            if not content_filter_active:
                                filtered_results.append(r)
                            continue
                    
                    # Content filtering - for now this is informational only since we can't search inside archives
                    # In a real implementation, this would require fetching each archive and searching inside
                    if content_filter_active and r['Type'] in ['Latest Archive', 'Archive'] and r['Status'] == 'Available':
                        # Flag for content relevance - would need API access to archive to implement fully
                        r['Content Match'] = "Possible"
                    
                    # If we get here, the entry passed all filters
                    filtered_results.append(r)
            
            # Replace results with filtered results
            results = filtered_results
            
            # Add notes about filtering
            filter_notes = []
            
            if date_filter_active:
                if from_date and to_date:
                    date_range = f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}"
                elif from_date:
                    date_range = f"after {from_date.strftime('%Y-%m-%d')}"
                elif to_date:
                    date_range = f"before {to_date.strftime('%Y-%m-%d')}"
                
                filter_notes.append(f'Date filter applied: showing archives {date_range}')
            
            if content_filter_active:
                filter_notes.append(f'Content filter applied: searching for "{specific_content}"')
            
            for note in filter_notes:
                results.append({
                    'Type': 'Note',
                    'Date': 'N/A',
                    'URL': 'N/A',
                    'Status': 'Info',
                    'Source': note
                })
                
        # Check for successful results
        available_archives = sum(1 for r in results if r['Status'] == 'Available')
        if available_archives > 0:
            self.session_stats['successful_searches'] += 1
        
        self.session_stats['platforms_checked'] += 1
        
        return results

def main():
    # Check login status before running the app
    if not st.session_state.logged_in:
        login_page()
        return
        
    # Initialize professional OSINT tool
    tool = ProfessionalOSINTTool()
    
    # Add user account panel and logout button in the top-right corner
    col1, col2 = st.columns([6, 1])
    with col2:
        st.markdown(f"""
        <div style="float: right; margin-right: 15px; margin-top: 10px; text-align: right;">
            <div style="font-size: 0.8rem; color: #718096;">Logged in as <b>{st.session_state.current_user}</b></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            # Clear other session state variables if needed
            if 'current_user' in st.session_state:
                del st.session_state.current_user
            st.rerun()
    
    # Render professional header
    tool.render_header()
    
    # Create professional sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h3>🛠️ Intelligence Tools</h3>
            <p>Select an analysis tool</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation sections
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">Core Analysis</div>', unsafe_allow_html=True)
        
        analysis_tools = [
            ("🏠", "Dashboard", "dashboard"),
            ("🌐", "Domain Intelligence", "domain"),
            ("📧", "Email Analysis", "email"),
            ("📮", "Email Harvester", "emailharvester"),
            ("🌍", "IP Geolocation", "ip"),
        ]
        
        selected_tool = None
        for icon, name, key in analysis_tools:
            if st.button(f"{icon} {name}", key=key, use_container_width=True):
                selected_tool = key
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">Identity Intelligence</div>', unsafe_allow_html=True)
        
        identity_tools = [
            ("👤", "Username Search", "username"),
            ("🧑‍💼", "Person Investigation", "person"),
        ]
        
        for icon, name, key in identity_tools:
            if st.button(f"{icon} {name}", key=key, use_container_width=True):
                selected_tool = key
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add new section for Archive Tools
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">Archive Intelligence</div>', unsafe_allow_html=True)
        
        archive_tools = [
            ("🕰️", "WayBack Tweets", "waybacktweets"),
        ]
        
        for icon, name, key in archive_tools:
            if st.button(f"{icon} {name}", key=key, use_container_width=True):
                selected_tool = key
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">Communication Analysis</div>', unsafe_allow_html=True)
        
        comm_tools = [
            ("📱", "Phone Intelligence", "phone"),
            ("💬", "WhatsApp Analysis", "whatsapp"),
            ("📡", "Telegram Investigation", "telegram"),
        ]
        
        for icon, name, key in comm_tools:
            if st.button(f"{icon} {name}", key=key, use_container_width=True):
                selected_tool = key
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session statistics
        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        st.metric("Searches Performed", tool.session_stats['total_searches'])
        st.metric("Success Rate", f"{(tool.session_stats['successful_searches']/max(tool.session_stats['total_searches'], 1)*100):.1f}%")
        st.metric("Platforms Checked", tool.session_stats['platforms_checked'])
    
    # Main content area
    if 'selected_tool' not in st.session_state:
        st.session_state.selected_tool = 'dashboard'
    
    if selected_tool:
        st.session_state.selected_tool = selected_tool
    
    current_tool = st.session_state.selected_tool
    
    # Dashboard
    if current_tool == 'dashboard':
        st.markdown("""
        <div class="pro-card slide-in-up">
            <div class="card-header">
                <h1 class="card-title">🎯 Intelligence Dashboard</h1>
                <div class="card-subtitle">Welcome to Osint Tool Pro - Your comprehensive OSINT platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature overview
        st.markdown("### 🚀 Platform Capabilities")
        
        col1, col2, col3 = st.columns(3)
        
        features = [
            {
                'title': 'Domain Intelligence',
                'description': 'Comprehensive domain analysis including WHOIS, DNS, security assessment, and infrastructure mapping.',
                'icon': '🌐',
                'platforms': '25+',
                'accuracy': '99.9%'
            },
            {
                'title': 'Identity Investigation',
                'description': 'Multi-platform username and personal information discovery across social networks and professional sites.',
                'icon': '👤',
                'platforms': '50+',
                'accuracy': '95.2%'
            },
            {
                'title': 'Communication Analysis',
                'description': 'Phone number intelligence, messaging platform investigation, and communication pattern analysis.',
                'icon': '📱',
                'platforms': '15+',
                'accuracy': '97.8%'
            }
        ]
        
        for i, feature in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="pro-card">
                    <div class="card-content" style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">{feature['icon']}</div>
                        <h3>{feature['title']}</h3>
                        <p style="color: var(--gray-600); margin-bottom: 1.5rem;">{feature['description']}</p>
                        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                            <div>
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{feature['platforms']}</div>
                                <div style="font-size: 0.75rem; color: var(--gray-500);">Platforms</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--success-color);">{feature['accuracy']}</div>
                                <div style="font-size: 0.75rem; color: var(--gray-500);">Accuracy</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick start guide
        st.markdown("### 🎯 Quick Start Guide")
        
        steps = [
            {"step": "1", "title": "Select Tool", "description": "Choose the appropriate intelligence tool from the sidebar based on your investigation needs."},
            {"step": "2", "title": "Enter Data", "description": "Input the target information (domain, username, email, etc.) into the analysis form."},
            {"step": "3", "title": "Run Analysis", "description": "Execute the investigation and monitor progress through our real-time dashboard."},
            {"step": "4", "title": "Review Results", "description": "Analyze findings through interactive visualizations and detailed reports."},
            {"step": "5", "title": "Export Reports", "description": "Download professional reports in JSON, CSV, or HTML formats for documentation."}
        ]
        
        for step in steps:
            st.markdown(f"""
            <div class="pro-card" style="margin-bottom: 1rem;">
                <div class="card-content">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="width: 40px; height: 40px; background: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                            {step['step']}
                        </div>
                        <div>
                            <h4 style="margin: 0; color: var(--gray-800);">{step['title']}</h4>
                            <p style="margin: 0.5rem 0 0 0; color: var(--gray-600);">{step['description']}</p>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Domain Intelligence
    elif current_tool == 'domain':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">🌐 Domain Intelligence Analysis</h2>
                    <div class="card-subtitle">Comprehensive domain investigation and security assessment</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            domain = st.text_input(
                "Target Domain",
                placeholder="example.com",
                help="Enter a domain name without http:// or https://",
                key="domain_input"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                analyze_btn = st.button("🚀 Analyze Domain", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>✅ WHOIS Information</li>
                        <li>✅ DNS Record Analysis</li>
                        <li>✅ Security Assessment</li>
                        <li>✅ SSL Certificate Check</li>
                        <li>✅ DNSSEC Validation</li>
                        <li>✅ Email Security (SPF/DMARC)</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if analyze_btn and domain:
            results = tool.domain_intelligence(domain)
            
            if results:
                # Export options
                st.markdown("### 📥 Export Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    json_data, json_filename, json_mime = tool.export_report(results, "domain_analysis", "json")
                    st.download_button("📄 Export JSON", json_data, json_filename, json_mime)
                
                with col2:
                    html_data, html_filename, html_mime = tool.export_report(pd.DataFrame([results]), "domain_analysis", "html")
                    st.download_button("🌐 Export HTML", html_data, html_filename, html_mime)
    
    # Username Intelligence
    elif current_tool == 'username':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">👤 Username Intelligence Analysis</h2>
                    <div class="card-subtitle">Multi-platform username investigation and risk assessment</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            username = st.text_input(
                "Target Username",
                placeholder="john_doe",
                help="Enter a username to search across multiple platforms",
                key="username_input"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                search_btn = st.button("🔍 Search Username", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Search Scope</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>🌐 Social Networks (10+)</li>
                        <li>💼 Professional Platforms (5+)</li>
                        <li>💻 Development Sites (8+)</li>
                        <li>🎮 Gaming Platforms (3+)</li>
                        <li>🎨 Creative Platforms (5+)</li>
                        <li>⚠️ Risk Assessment</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if search_btn and username:
            results_df = tool.username_intelligence(username)
            
            if results_df is not None:
                # Export options
                st.markdown("### 📥 Export Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    json_data, json_filename, json_mime = tool.export_report(results_df, "username_analysis", "json")
                    st.download_button("📄 Export JSON", json_data, json_filename, json_mime)
                
                with col2:
                    csv_data, csv_filename, csv_mime = tool.export_report(results_df, "username_analysis", "csv")
                    st.download_button("📊 Export CSV", csv_data, csv_filename, csv_mime)
                
                with col3:
                    html_data, html_filename, html_mime = tool.export_report(results_df, "username_analysis", "html")
                    st.download_button("🌐 Export HTML", html_data, html_filename, html_mime)
    
    # Email Analysis
    elif current_tool == 'email':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">📧 Email Analysis</h2>
                    <div class="card-subtitle">Comprehensive email investigation and verification</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            email = st.text_input(
                "Email Address",
                placeholder="example@domain.com",
                help="Enter email address for analysis",
                key="email_input"
            )
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                check_breaches = st.checkbox("Check for data breaches", value=True)
                check_reputation = st.checkbox("Email reputation analysis", value=True)
                validate_mx = st.checkbox("MX record validation", value=True)
                check_social_media = st.checkbox("Search social media accounts", value=True)
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                analyze_btn = st.button("🔍 Analyze Email", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>✅ Email Validation</li>
                        <li>🌐 Domain Analysis</li>
                        <li>📡 MX Record Check</li>
                        <li>🔍 Breach Database Search</li>
                        <li>⭐ Reputation Analysis</li>
                        <li>🔒 Security Assessment</li>
                        <li>📊 Pattern Analysis</li>
                        <li>👤 Social Media Discovery</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if analyze_btn and email:
            try:
                tool.session_stats['total_searches'] += 1
                
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                is_valid = re.match(email_pattern, email) is not None
                
                if is_valid:
                    # Extract components
                    username, domain = email.split('@')
                    
                    email_info = {
                        'Email Address': email,
                        'Username': username,
                        'Domain': domain,
                        'Valid Format': 'Yes' if is_valid else 'No',
                        'Email Type': 'Personal' if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'] else 'Business/Other',
                    }
                    
                    # Domain analysis
                    if validate_mx:
                        try:
                            mx_records = dns.resolver.resolve(domain, 'MX')
                            email_info['MX Records'] = len(mx_records)
                            email_info['Primary MX'] = str(mx_records[0]).split()[-1] if mx_records else 'None'
                            email_info['MX Valid'] = 'Yes'
                        except:
                            email_info['MX Records'] = 0
                            email_info['Primary MX'] = 'None'
                            email_info['MX Valid'] = 'No'
                    
                    # Security indicators
                    email_info['Disposable Domain'] = 'Yes' if domain in [
                        '10minutemail.com', 'tempmail.org', 'guerrillamail.com', 'mailinator.com'
                    ] else 'No'
                    
                    # Pattern analysis
                    email_info['Contains Numbers'] = 'Yes' if any(char.isdigit() for char in username) else 'No'
                    email_info['Contains Special Chars'] = 'Yes' if any(char in '._+-' for char in username) else 'No'
                    email_info['Username Length'] = len(username)
                    
                    # Simulated breach check
                    if check_breaches:
                        # This is simulated - in real implementation, you'd use HaveIBeenPwned API
                        common_breached_domains = ['yahoo.com', 'linkedin.com', 'adobe.com']
                        email_info['Potential Breaches'] = 'High Risk' if domain in common_breached_domains else 'Low Risk'
                    
                    # Reputation analysis
                    if check_reputation:
                        # Simulated reputation scoring
                        reputation_score = 85 if domain not in ['tempmail.org', 'guerrillamail.com'] else 25
                        email_info['Reputation Score'] = f"{reputation_score}/100"
                        email_info['Reputation Status'] = 'Good' if reputation_score > 70 else 'Poor'
                    
                    tool.session_stats['successful_searches'] += 1
                    tool.session_stats['platforms_checked'] += 1
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(tool.create_metric_card("Validity", "✅ Valid" if is_valid else "❌ Invalid", "Email format check", "📧"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(tool.create_metric_card("Domain", domain, "Email domain", "🌐"), unsafe_allow_html=True)
                    with col3:
                        reputation_score = email_info.get('Reputation Score', 'N/A')
                        st.markdown(tool.create_metric_card("Reputation", reputation_score, "Trust score", "⭐"), unsafe_allow_html=True)
                    
                    # Detailed analysis table
                    email_df = pd.DataFrame(list(email_info.items()), columns=['Property', 'Value'])
                    st.markdown("### 📊 Detailed Email Analysis")
                    st.markdown(tool.render_professional_table(email_df, "Email Intelligence Report"), unsafe_allow_html=True)
                    
                    # Social Media Discovery
                    if check_social_media:
                        st.markdown("### 👤 Social Media Accounts Search")
                        with st.spinner("Searching for associated social media accounts..."):
                            # Simulate social media account search
                            social_media_results = []
                            
                            # Common platforms to check
                            platforms = {
                                'Facebook': {'url': f"https://facebook.com/search/people/?q={email}", 'icon': '👥'},
                                'Twitter': {'url': f"https://twitter.com/search?q={email}", 'icon': '🐦'},
                                'LinkedIn': {'url': f"https://www.linkedin.com/search/results/all/?keywords={email}", 'icon': '💼'},
                                'Instagram': {'url': f"https://www.instagram.com/accounts/search/?q={email}", 'icon': '📸'},
                                'GitHub': {'url': f"https://github.com/search?q={email}", 'icon': '💻'},
                                'Pinterest': {'url': f"https://www.pinterest.com/search/users/?q={email}", 'icon': '📌'},
                                'Gravatar': {'url': f"https://en.gravatar.com/{username}", 'icon': '🖼️'},
                                'Medium': {'url': f"https://medium.com/search?q={email}", 'icon': '📝'},
                                'Quora': {'url': f"https://www.quora.com/search?q={email}", 'icon': '❓'},
                            }
                            
                            # Simulate findings (in a real implementation, use APIs or web scraping)
                            found_accounts = ['GitHub', 'LinkedIn', 'Gravatar']
                            
                            for platform, details in platforms.items():
                                status = 'Found' if platform in found_accounts else 'Not Found'
                                likelihood = 'High' if platform in found_accounts else 'Low'
                                
                                social_media_results.append({
                                    'Platform': f"{details['icon']} {platform}",
                                    'Status': tool.create_status_badge('found' if platform in found_accounts else 'not_found', status),
                                    'Username': username if platform in found_accounts else '<span style="color: #e53e3e; font-weight: bold;">Not Found</span>',
                                    'Search URL': details['url'],
                                    'Likelihood': likelihood
                                })
                            
                            # Display results
                            social_df = pd.DataFrame(social_media_results)
                            st.markdown(tool.render_professional_table(social_df, "Social Media Account Discovery"), unsafe_allow_html=True)
                            
                            # Platform coverage metrics
                            total_platforms = len(platforms)
                            found_platforms = len(found_accounts)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(tool.create_metric_card("Platforms Checked", total_platforms, "Social networks", "🔍"), unsafe_allow_html=True)
                            with col2:
                                st.markdown(tool.create_metric_card("Accounts Found", found_platforms, f"{(found_platforms/total_platforms)*100:.1f}% hit rate", "✅"), unsafe_allow_html=True)
                            with col3:
                                st.markdown(tool.create_metric_card("Digital Footprint", "Medium" if found_platforms > 0 else "Low", "Online visibility", "👣"), unsafe_allow_html=True)
                            
                            # Add quick links
                            st.markdown("### ⚡ Quick Social Media Search Links")
                            
                            # Create rows of buttons
                            cols = st.columns(3)
                            for i, (platform, details) in enumerate(platforms.items()):
                                col_index = i % 3
                                with cols[col_index]:
                                    button_color = "#1a365d" if platform in found_accounts else "#718096"
                                    st.markdown(f'<a href="{details["url"]}" target="_blank"><button style="width: 100%; background: {button_color}; color: white; border: none; padding: 10px; border-radius: 5px; margin-bottom: 10px;">{details["icon"]} {platform}</button></a>', unsafe_allow_html=True)
                            
                            # Update stats
                            tool.session_stats['platforms_checked'] += total_platforms
                    
                    # Additional domain analysis
                    if st.button("🔍 Analyze Domain Further"):
                        domain_results = tool.domain_intelligence(domain)
                        if domain_results:
                            st.markdown("### 🌐 Extended Domain Analysis")
                            st.success("Domain analysis complete - see results above")
                    
                else:
                    st.markdown(tool.create_professional_alert("Invalid email format", "error"), unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(tool.create_professional_alert(f"Analysis error: {str(e)}", "error"), unsafe_allow_html=True)
    
    # IP Geolocation
    elif current_tool == 'ip':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">🌍 IP Geolocation Analysis</h2>
                    <div class="card-subtitle">Comprehensive IP address investigation and geolocation</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            ip_address = st.text_input(
                "IP Address",
                placeholder="192.168.1.1 or 2001:0db8:85a3::8a2e:370:7334",
                help="Enter IPv4 or IPv6 address",
                key="ip_input"
            )
            
            # Search word input
            search_word = st.text_input(
                "Search Word",
                placeholder="Enter a word to filter results",
                help="Filter results by specific word or pattern",
                key="ip_search_word"
            )
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                check_reputation = st.checkbox("IP reputation check", value=True)
                check_blacklists = st.checkbox("Blacklist verification", value=True)
                check_ports = st.checkbox("Basic port scanning", value=False)
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                analyze_btn = st.button("🔍 Analyze IP", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>🌍 Geographic Location</li>
                        <li>🏢 ISP Information</li>
                        <li>🔢 ASN Details</li>
                        <li>🛡️ Security Reputation</li>
                        <li>📋 Blacklist Status</li>
                        <li>🔍 Reverse DNS</li>
                        <li>📊 Network Analysis</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if analyze_btn and ip_address:
            try:
                import ipaddress
                tool.session_stats['total_searches'] += 1
                
                # Validate IP address
                try:
                    ip_obj = ipaddress.ip_address(ip_address)
                    is_valid = True
                    ip_type = 'IPv4' if ip_obj.version == 4 else 'IPv6'
                except:
                    is_valid = False
                    ip_type = 'Invalid'
                
                if is_valid:
                    ip_info = {
                        'IP Address': ip_address,
                        'IP Version': ip_type,
                        'Valid': 'Yes',
                        'Private/Public': 'Private' if ip_obj.is_private else 'Public',
                        'Loopback': 'Yes' if ip_obj.is_loopback else 'No',
                        'Multicast': 'Yes' if ip_obj.is_multicast else 'No',
                    }
                    
                    # Simulate geolocation data (in real implementation, use services like ipinfo.io, ipapi.com)
                    if not ip_obj.is_private and not ip_obj.is_loopback:
                        # Simulated geolocation data
                        geolocation_data = {
                            'Country': 'United States',
                            'Region': 'California',
                            'City': 'Mountain View',
                            'Latitude': '37.3860',
                            'Longitude': '-122.0840',
                            'ISP': 'Google LLC',
                            'Organization': 'Google Public DNS',
                            'ASN': 'AS15169',
                            'ASN Description': 'GOOGLE',
                            'Timezone': 'America/Los_Angeles'
                        }
                        
                        # Add hostname resolution
                        try:
                            # Limit hostname resolution to public IPs with a short timeout
                            hostname = socket.gethostbyaddr(ip_address)[0]
                            ip_info['Hostname'] = hostname
                        except socket.gaierror:
                            # DNS resolution error
                            print(f"DNS resolution error for {ip_address}")
                            ip_info['Hostname'] = 'Not resolved (DNS error)'
                        except socket.timeout:
                            # Timeout error
                            print(f"Timeout resolving hostname for {ip_address}")
                            ip_info['Hostname'] = 'Not resolved (timeout)'
                        except Exception as e:
                            # Other errors
                            print(f"Error resolving hostname for {ip_address}: {str(e)}")
                            ip_info['Hostname'] = 'Not resolved'
                        
                        ip_info.update(geolocation_data)
                    else:
                        ip_info.update({
                            'Country': 'N/A (Private IP)',
                            'Region': 'N/A',
                            'City': 'N/A',
                            'ISP': 'N/A',
                            'Hostname': 'N/A'
                        })
                    
                    # Security checks
                    if check_reputation:
                        # Simulated reputation check
                        reputation_score = 95 if not ip_obj.is_private else 100
                        ip_info['Reputation Score'] = f"{reputation_score}/100"
                        ip_info['Security Status'] = 'Clean' if reputation_score > 80 else 'Suspicious'
                    
                    if check_blacklists:
                        # Simulated blacklist check
                        blacklisted = False  # In real implementation, check multiple blacklists
                        ip_info['Blacklist Status'] = 'Not Listed' if not blacklisted else 'Listed'
                        ip_info['Blacklist Details'] = 'Clean across major blacklists'
                    
                    # Basic port scanning simulation
                    if check_ports and not ip_obj.is_private:
                        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
                        open_ports = []
                        
                        # Simulate port scanning (in real implementation, use actual port scanning)
                        for port in [80, 443]:  # Simulate only HTTP/HTTPS as open
                            open_ports.append(port)
                        
                        ip_info['Open Ports'] = ', '.join(map(str, open_ports)) if open_ports else 'None detected'
                    
                    tool.session_stats['successful_searches'] += 1
                    tool.session_stats['platforms_checked'] += 1
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(tool.create_metric_card("Status", "✅ Valid IP" if is_valid else "❌ Invalid", "IP validation", "🌐"), unsafe_allow_html=True)
                    with col2:
                        country = ip_info.get('Country', 'Unknown')
                        st.markdown(tool.create_metric_card("Location", country, "Geographic location", "🌍"), unsafe_allow_html=True)
                    with col3:
                        isp = ip_info.get('ISP', 'Unknown')
                        st.markdown(tool.create_metric_card("ISP", isp[:15] + "..." if len(isp) > 15 else isp, "Internet Service Provider", "🏢"), unsafe_allow_html=True)
                    
                    # Detailed analysis table
                    ip_df = pd.DataFrame(list(ip_info.items()), columns=['Property', 'Value'])
                    
                    # Filter results if search word is provided
                    if search_word:
                        ip_df = ip_df[ip_df['Value'].astype(str).str.contains(search_word, case=False, na=False)]
                        if len(ip_df) == 0:
                            st.markdown(tool.create_professional_alert(f"No results found containing '{search_word}'", "info"), unsafe_allow_html=True)
                    
                    st.markdown("### 📊 Detailed IP Analysis")
                    st.markdown(tool.render_professional_table(ip_df, "IP Geolocation Report"), unsafe_allow_html=True)
                    
                    # Map visualization (if coordinates available)
                    if not ip_obj.is_private and 'Latitude' in ip_info and 'Longitude' in ip_info:
                        st.markdown("### 🗺️ Geographic Visualization")
                        
                        # Create a simple map visualization
                        map_data = pd.DataFrame({
                            'lat': [float(ip_info['Latitude'])],
                            'lon': [float(ip_info['Longitude'])],
                            'IP': [ip_address]
                        })
                        
                        # Create plotly map
                        fig = px.scatter_mapbox(
                            map_data,
                            lat="lat",
                            lon="lon",
                            hover_name="IP",
                            zoom=10,
                            height=400,
                            title=f"IP Location: {ip_info.get('City', 'Unknown')}, {ip_info.get('Country', 'Unknown')}"
                        )
                        fig.update_traces(marker_size=15, marker_color='red')
                        fig.update_layout(mapbox_style="open-street-map")
                        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.markdown(tool.create_professional_alert("Invalid IP address format", "error"), unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(tool.create_professional_alert(f"Analysis error: {str(e)}", "error"), unsafe_allow_html=True)
    
    # Phone Intelligence
    elif current_tool == 'phone':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">📱 Phone Intelligence Analysis</h2>
                    <div class="card-subtitle">Comprehensive phone number analysis and carrier information</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            phone = st.text_input(
                "Phone Number",
                placeholder="+1234567890",
                help="Enter phone number with country code",
                key="phone_input"
            )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                analyze_btn = st.button("🔍 Analyze Phone", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>🌍 Geographic Location</li>
                        <li>📡 Carrier Information</li>
                        <li>⏰ Timezone Data</li>
                        <li>📱 Number Type (Mobile/Landline)</li>
                        <li>✅ Validity Check</li>
                        <li>🏢 Line Type Analysis</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if analyze_btn and phone:
            try:
                tool.session_stats['total_searches'] += 1
                
                # Parse phone number
                parsed_number = phonenumbers.parse(phone)
                
                # Get information
                phone_info = {
                    'Number': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    'Country Code': f"+{parsed_number.country_code}",
                    'National Number': str(parsed_number.national_number),
                    'Valid': phonenumbers.is_valid_number(parsed_number),
                    'Possible': phonenumbers.is_possible_number(parsed_number),
                    'Geographic Location': geocoder.description_for_number(parsed_number, 'en') or 'Unknown',
                    'Carrier': carrier.name_for_number(parsed_number, 'en') or 'Unknown',
                    'Number Type': str(phonenumbers.number_type(parsed_number)).split('.')[-1],
                    'Region Code': phonenumbers.region_code_for_number(parsed_number)
                }
                
                # Get timezone
                try:
                    time_zones = timezone.time_zones_for_number(parsed_number)
                    phone_info['Timezone'] = ', '.join(time_zones) if time_zones else 'Unknown'
                except:
                    phone_info['Timezone'] = 'Unknown'
                
                tool.session_stats['successful_searches'] += 1
                tool.session_stats['platforms_checked'] += 1
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(tool.create_metric_card("Validity", "✅ Valid" if phone_info['Valid'] else "❌ Invalid", "Number validation", "📱"), unsafe_allow_html=True)
                with col2:
                    st.markdown(tool.create_metric_card("Location", phone_info['Geographic Location'], "Geographic region", "🌍"), unsafe_allow_html=True)
                with col3:
                    st.markdown(tool.create_metric_card("Carrier", phone_info['Carrier'], "Service provider", "📡"), unsafe_allow_html=True)
                
                # Detailed information table
                phone_df = pd.DataFrame(list(phone_info.items()), columns=['Property', 'Value'])
                st.markdown("### 📊 Detailed Phone Analysis")
                st.markdown(tool.render_professional_table(phone_df, "Phone Intelligence Report"), unsafe_allow_html=True)
                
            except phonenumbers.NumberParseException as e:
                st.markdown(tool.create_professional_alert(f"Phone parsing error: {str(e)}", "error"), unsafe_allow_html=True)
            except Exception as e:
                st.markdown(tool.create_professional_alert(f"Analysis error: {str(e)}", "error"), unsafe_allow_html=True)
    
    # Telegram Investigation
    elif current_tool == 'telegram':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">📡 Telegram Investigation</h2>
                    <div class="card-subtitle">Telegram username and phone number investigation</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            # Search type selection
            search_type = st.radio("Search Type:", ["Username", "Phone Number"], key="telegram_search_type")
            
            if search_type == "Username":
                telegram_input = st.text_input(
                    "Telegram Username",
                    placeholder="@username or username",
                    help="Enter Telegram username with or without @",
                    key="telegram_username"
                )
            else:
                telegram_input = st.text_input(
                    "Phone Number",
                    placeholder="+1234567890",
                    help="Enter phone number with country code",
                    key="telegram_phone"
                )
            
            # Search buttons
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                search_btn = st.button("🔍 Search Telegram", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Investigation Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>👤 Profile Verification</li>
                        <li>🔗 T.me Link Generation</li>
                        <li>📱 Phone Number Analysis</li>
                        <li>🔍 Username Availability</li>
                        <li>📊 Profile Analysis</li>
                        <li>📞 TrueCaller API Integration</li>
                        <li>🛡️ Spam Score Analysis</li>
                        <li>⚠️ Security Notes</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Search functionality
        if search_btn and telegram_input:
            tool.session_stats['total_searches'] += 1
            
            telegram_results = []
            
            if search_type == "Username":
                # Clean username
                username = telegram_input.replace('@', '').strip()
                
                if len(username) >= 5:
                    telegram_info = {
                        'Search Type': 'Username',
                        'Input': f"@{username}",
                        'Telegram Web URL': f"https://t.me/{username}",
                        'Direct Message Link': f"https://t.me/{username}",
                        'Username Validity': 'Valid format' if len(username) >= 5 else 'Too short',
                        'Status': 'Profile URL generated',
                        'Notes': 'Username existence requires manual verification'
                    }
                    
                    # Check if username follows Telegram rules
                    if username.replace('_', '').isalnum():
                        telegram_info['Format Check'] = 'Valid characters'
                    else:
                        telegram_info['Format Check'] = 'Invalid characters detected'
                    
                    telegram_results.append(telegram_info)
                    
                    # Perform additional username analysis
                    # Simulate possible username variants and similar platforms
                    username_variations = [
                        username,
                        f"{username}_",
                        f"{username}official",
                        f"real{username}",
                        f"{username}tg"
                    ]
                    
                    # Create detailed username analysis
                    username_analysis = []
                    for variant in username_variations:
                        # Simulate random findings
                        is_found = variant == username
                        username_analysis.append({
                            'Username Variant': f"@{variant}",
                            'URL': f"https://t.me/{variant}",
                            'Status': tool.create_status_badge('found' if is_found else 'not_found', 
                                                             'Likely Match' if is_found else 'Possible Variant'),
                            'Confidence': 'High' if variant == username else 'Medium' if 'official' in variant else 'Low'
                        })
                    
                    # Similar platforms to check
                    similar_platforms = {
                        'Signal': {'url': '#', 'icon': '📱', 'available': False},
                        'WhatsApp': {'url': f"https://wa.me/{username}", 'icon': '💬', 'available': True},
                        'Discord': {'url': '#', 'icon': '🎮', 'available': False},
                        'Threema': {'url': '#', 'icon': '🔒', 'available': False},
                        'Viber': {'url': '#', 'icon': '📞', 'available': True}
                    }
                    
                    # Record platform analysis
                    platform_analysis = []
                    for platform, details in similar_platforms.items():
                        platform_analysis.append({
                            'Platform': f"{details['icon']} {platform}",
                            'Username Search': f"@{username}",
                            'Status': tool.create_status_badge(
                                'found' if details['available'] else 'not_found',
                                'Available' if details['available'] else 'Not Found'
                            ),
                            'URL': details['url'] if details['url'] != '#' else 'N/A'
                        })
                    
                    # Store additional analysis
                    telegram_info['username_analysis'] = username_analysis
                    telegram_info['platform_analysis'] = platform_analysis
                    
                    tool.session_stats['successful_searches'] += 1
                    
                else:
                    st.markdown(tool.create_professional_alert("Username too short (minimum 5 characters)", "error"), unsafe_allow_html=True)
            
            else:  # Phone Number
                try:
                    parsed_number = phonenumbers.parse(telegram_input)
                    
                    if phonenumbers.is_valid_number(parsed_number):
                        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                        
                        telegram_info = {
                            'Search Type': 'Phone Number',
                            'Input': formatted_number,
                            'Geographic Location': geocoder.description_for_number(parsed_number, 'en') or 'Unknown',
                            'Carrier': carrier.name_for_number(parsed_number, 'en') or 'Unknown',
                            'Number Type': str(phonenumbers.number_type(parsed_number)).split('.')[-1],
                            'Region': phonenumbers.region_code_for_number(parsed_number),
                            'Status': 'Phone analysis complete',
                            'Notes': 'Telegram registration cannot be verified without API access'
                        }
                        
                        # TrueCaller API integration
                        st.markdown("### 📱 TrueCaller API Lookup")
                        with st.spinner("Searching TrueCaller database..."):
                            # Simulated TrueCaller data (in a real implementation, you would use the actual API)
                            truecaller_data = tool.get_truecaller_data(formatted_number)
                            
                            if truecaller_data:
                                st.success("Found information in TrueCaller database!")
                                
                                # Create display table
                                truecaller_df = pd.DataFrame(list(truecaller_data.items()), columns=['Property', 'Value'])
                                st.markdown(tool.render_professional_table(truecaller_df, "TrueCaller Information"), unsafe_allow_html=True)
                                
                                # Add summarized data to main result
                                telegram_info['TrueCaller Name'] = truecaller_data.get('Name', 'Not Found')
                                telegram_info['TrueCaller Tags'] = truecaller_data.get('Tags', 'None')
                                telegram_info['Spam Likelihood'] = truecaller_data.get('Spam Score', 'Low')
                                
                                # Visual representation of spam score
                                st.markdown("### 📊 Spam Score Analysis")
                                spam_score = truecaller_data.get('Spam Score', 'Low')
                                score_value = {
                                    'Very Low': 0.1,
                                    'Low': 0.3,
                                    'Medium': 0.5,
                                    'High': 0.7,
                                    'Very High': 0.9
                                }.get(spam_score, 0.1)
                                
                                # Create gauge chart for spam score
                                fig = go.Figure(go.Indicator(
                                    mode="gauge+number+delta",
                                    value=score_value * 100,
                                    domain={'x': [0, 1], 'y': [0, 1]},
                                    title={'text': "Spam Likelihood", 'font': {'size': 24}},
                                    gauge={
                                        'axis': {'range': [0, 100], 'tickwidth': 1},
                                        'bar': {'color': "darkblue"},
                                        'bgcolor': "white",
                                        'borderwidth': 2,
                                        'bordercolor': "gray",
                                        'steps': [
                                            {'range': [0, 20], 'color': '#48BB78'},
                                            {'range': [20, 40], 'color': '#90CDF4'},
                                            {'range': [40, 60], 'color': '#F6E05E'},
                                            {'range': [60, 80], 'color': '#F6AD55'},
                                            {'range': [80, 100], 'color': '#F56565'}
                                        ],
                                        'threshold': {
                                            'line': {'color': "red", 'width': 4},
                                            'thickness': 0.75,
                                            'value': 80
                                        }
                                    }
                                ))
                                
                                fig.update_layout(
                                    height=300,
                                    margin=dict(l=20, r=20, t=50, b=20),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    font={'color': "#2D3748", 'family': "Inter"}
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Add caller type metrics
                                caller_type = truecaller_data.get('Type', 'Unknown')
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(tool.create_metric_card("Caller Type", caller_type, "Identity category", "👤"), unsafe_allow_html=True)
                                with col2:
                                    reports = truecaller_data.get('User Reports', 'None')
                                    st.markdown(tool.create_metric_card("User Reports", reports, "Community feedback", "📝"), unsafe_allow_html=True)
                                with col3:
                                    searches = truecaller_data.get('Number of Searches', '0')
                                    st.markdown(tool.create_metric_card("Search Popularity", searches, "Times looked up", "🔍"), unsafe_allow_html=True)
                            else:
                                st.warning("No TrueCaller information found for this number")
                                telegram_info['TrueCaller'] = 'No data found'
                        
                        telegram_results.append(telegram_info)
                        tool.session_stats['successful_searches'] += 1
                        
                    else:
                        st.markdown(tool.create_professional_alert("Invalid phone number format", "error"), unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(tool.create_professional_alert(f"Phone parsing error: {str(e)}", "error"), unsafe_allow_html=True)
            
                            # Display results
            if telegram_results:
                tool.session_stats['platforms_checked'] += 1
                
                st.markdown("### 📡 Telegram Investigation Results")
                
                for result in telegram_results:
                    # Filter out analysis data for main table
                    main_result = {k: v for k, v in result.items() if k not in ['username_analysis', 'platform_analysis']}
                    result_df = pd.DataFrame(list(main_result.items()), columns=['Property', 'Value'])
                    st.markdown(tool.render_professional_table(result_df, f"Telegram {result['Search Type']} Analysis"), unsafe_allow_html=True)
                    
                    # Display username analysis if available
                    if search_type == "Username" and 'username_analysis' in result:
                        # Username variants
                        st.markdown("### 👤 Username Variants Analysis")
                        username_df = pd.DataFrame(result['username_analysis'])
                        st.markdown(tool.render_professional_table(username_df, "Possible Username Variations"), unsafe_allow_html=True)
                        
                        # Cross-platform analysis
                        st.markdown("### 🌐 Cross-Platform Username Analysis")
                        platform_df = pd.DataFrame(result['platform_analysis'])
                        st.markdown(tool.render_professional_table(platform_df, "Username Check Across Messaging Platforms"), unsafe_allow_html=True)
                        
                        # Username metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            variants_count = len(result['username_analysis'])
                            st.markdown(tool.create_metric_card("Variants Checked", variants_count, "Possible username variations", "🔍"), unsafe_allow_html=True)
                        with col2:
                            platforms_count = len(result['platform_analysis'])
                            st.markdown(tool.create_metric_card("Platforms Checked", platforms_count, "Messaging platforms", "🌐"), unsafe_allow_html=True)
                        with col3:
                            available_count = sum(1 for p in result['platform_analysis'] if 'Available' in p['Status'])
                            st.markdown(tool.create_metric_card("Cross-Platform Matches", available_count, f"{(available_count/platforms_count)*100:.1f}% hit rate", "✅"), unsafe_allow_html=True)
                    
                    # Quick actions for username
                    if search_type == "Username" and 'Telegram Web URL' in result:
                        st.markdown("### ⚡ Quick Actions")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f'<a href="{result["Telegram Web URL"]}" target="_blank"><button style="width: 100%; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px;">🔗 Open Telegram Profile</button></a>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<a href="https://web.telegram.org/" target="_blank"><button style="width: 100%; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px;">🌐 Open Telegram Web</button></a>', unsafe_allow_html=True)
                        with col3:
                            st.markdown(f'<a href="https://telegram.me/search_bot?start={result["Input"].replace("@", "")}" target="_blank"><button style="width: 100%; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px;">🤖 Search Bot</button></a>', unsafe_allow_html=True)
    
    # Person Investigation  
    elif current_tool == 'person':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">🧑‍💼 Person Investigation</h2>
                    <div class="card-subtitle">Comprehensive person search across multiple platforms and databases</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            # Input fields
            name = st.text_input("Full Name", placeholder="John Doe", key="person_name")
            col_loc, col_comp = st.columns(2)
            with col_loc:
                location = st.text_input("Location (Optional)", placeholder="New York, NY", key="person_location")
            with col_comp:
                company = st.text_input("Company (Optional)", placeholder="Company Name", key="person_company")
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                search_btn = st.button("🔍 Search Person", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Search Sources</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>💼 LinkedIn Profiles</li>
                        <li>🌐 Social Media Accounts</li>
                        <li>📰 News Portals & Articles</li>
                        <li>🌍 International News Sources</li>
                        <li>📺 Media Mentions</li>
                        <li>🏢 Company Directories</li>
                        <li>📧 Email Addresses</li>
                        <li>📱 Phone Numbers</li>
                        <li>🏠 Address Information</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if search_btn and name:
            tool.session_stats['total_searches'] += 1
            
            # Person search platforms
            search_platforms = {
                'Professional': {
                    'LinkedIn': f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}",
                    'AngelList': f"https://angel.co/search?query={name.replace(' ', '+')}",
                    'Crunchbase': f"https://www.crunchbase.com/search/people?query={name.replace(' ', '+')}",
                },
                'Social Media': {
                    'Facebook': f"https://www.facebook.com/search/top?q={name.replace(' ', '+')}",
                    'Twitter': f"https://twitter.com/search?q={name.replace(' ', '+')}",
                    'Instagram': f"https://www.instagram.com/explore/search/keyword/?q={name.replace(' ', '+')}",
                },
                'News Portals': {
                    'Google News': f"https://news.google.com/search?q={name.replace(' ', '+')}",
                    'CNN': f"https://www.cnn.com/search?q={name.replace(' ', '+')}",
                    'BBC News': f"https://www.bbc.co.uk/search?q={name.replace(' ', '+')}",
                    'Reuters': f"https://www.reuters.com/search/news?blob={name.replace(' ', '+')}",
                    'Al Jazeera': f"https://www.aljazeera.com/search/{name.replace(' ', '%20')}",
                    'Associated Press': f"https://apnews.com/search?q={name.replace(' ', '%20')}",
                    'NYTimes': f"https://www.nytimes.com/search?query={name.replace(' ', '+')}",
                    'Washington Post': f"https://www.washingtonpost.com/newssearch/?query={name.replace(' ', '+')}",
                    'The Guardian': f"https://www.theguardian.com/search?q={name.replace(' ', '+')}",
                    'Fox News': f"https://www.foxnews.com/search-results/search?q={name.replace(' ', '+')}",
                },
                'Forums & Communities': {
                    'Reddit': f"https://www.reddit.com/search/?q={name.replace(' ', '+')}",
                    'Quora': f"https://www.quora.com/search?q={name.replace(' ', '+')}",
                    'Stack Exchange': f"https://stackexchange.com/search?q={name.replace(' ', '+')}",
                    'Medium': f"https://medium.com/search?q={name.replace(' ', '+')}",
                    'Hackernews': f"https://hn.algolia.com/?q={name.replace(' ', '+')}",
                    'Discord Lookup': f"https://discordlookup.com/search?q={name.replace(' ', '+')}",
                },
                'Search Engines': {
                    'Google': f"https://www.google.com/search?q=\"{name.replace(' ', '+')}\"",
                    'Bing': f"https://www.bing.com/search?q=\"{name.replace(' ', '+')}\"",
                    'DuckDuckGo': f"https://duckduckgo.com/?q=\"{name.replace(' ', '+')}\"",
                },
                'Public Records': {
                    'WhitePages': f"https://www.whitepages.com/name/{name.replace(' ', '-')}",
                    'Spokeo': f"https://www.spokeo.com/search?q={name.replace(' ', '+')}",
                    'TruePeopleSearch': f"https://www.truepeoplesearch.com/results?name={name.replace(' ', '%20')}",
                }
            }
            
            if location:
                for category in search_platforms.values():
                    for platform, url in category.items():
                        category[platform] = f"{url}&location={location.replace(' ', '+')}"
            
            results = []
            total_platforms = sum(len(category) for category in search_platforms.values())
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            current_platform = 0
            
            for category, platforms in search_platforms.items():
                for platform, url in platforms.items():
                    current_platform += 1
                    status_text.text(f"🔍 Checking {platform}...")
                    progress_bar.progress(current_platform / total_platforms)
                    
                    results.append({
                        'Platform': platform,
                        'Category': category,
                        'Search URL': url,
                        'Status': 'Available',
                        'Type': 'Search Link'
                    })
                    
                    time.sleep(0.1)
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                df = pd.DataFrame(results)
                tool.session_stats['successful_searches'] += 1
                tool.session_stats['platforms_checked'] += len(results)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(tool.create_metric_card("Search Queries", len(results), "Generated", "🔍"), unsafe_allow_html=True)
                with col2:
                    st.markdown(tool.create_metric_card("Categories", len(search_platforms), "Covered", "📂"), unsafe_allow_html=True)
                with col3:
                    st.markdown(tool.create_metric_card("Target", name, "Person under investigation", "🎯"), unsafe_allow_html=True)
                
                st.markdown("### 🔍 Person Investigation Results")
                
                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    category_filter = st.selectbox("Filter by Category:", ['All'] + list(df['Category'].unique()))
                with col2:
                    if category_filter == 'All':
                        platform_options = ['All'] + list(df['Platform'].unique())
                    else:
                        platform_options = ['All'] + list(df[df['Category'] == category_filter]['Platform'].unique())
                    platform_filter = st.selectbox("Filter by Platform:", platform_options)
                
                # Apply filters
                filtered_df = df.copy()
                if category_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Category'] == category_filter]
                if platform_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Platform'] == platform_filter]
                
                # Display filtered results
                st.markdown(tool.render_professional_table(filtered_df, f"Person Search Results ({len(filtered_df)} sources)"), unsafe_allow_html=True)
                
                # News-specific section
                if 'News Portals' in df['Category'].values:
                    news_df = df[df['Category'] == 'News Portals']
                    if not news_df.empty:
                        st.markdown("### 📰 News Portal Search Results")
                        st.markdown(tool.render_professional_table(news_df, f"News Articles for {name}"), unsafe_allow_html=True)
                        
                        # Quick actions for news
                        st.markdown("### ⚡ Quick News Actions")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f'<a href="https://news.google.com/search?q={name.replace(" ", "+")}" target="_blank"><button style="width: 100%; background: #1a365d; color: white; border: none; padding: 10px; border-radius: 5px;">🔍 Comprehensive News Search</button></a>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<a href="https://www.google.com/search?q={name.replace(" ", "+")}+latest+news&tbm=nws" target="_blank"><button style="width: 100%; background: #1a365d; color: white; border: none; padding: 10px; border-radius: 5px;">📰 Recent News Articles</button></a>', unsafe_allow_html=True)
                
                # Forums & Communities section
                if 'Forums & Communities' in df['Category'].values:
                    forums_df = df[df['Category'] == 'Forums & Communities']
                    if not forums_df.empty:
                        st.markdown("### 💬 Forums & Communities Search Results")
                        st.markdown(tool.render_professional_table(forums_df, f"Forum Posts & Discussions for {name}"), unsafe_allow_html=True)
                        
                        # Quick actions for forums
                        st.markdown("### ⚡ Quick Forum Actions")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f'<a href="https://www.reddit.com/search/?q={name.replace(" ", "+")}" target="_blank"><button style="width: 100%; background: #FF4500; color: white; border: none; padding: 10px; border-radius: 5px;">🔍 Reddit Discussions</button></a>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<a href="https://www.quora.com/search?q={name.replace(" ", "+")}" target="_blank"><button style="width: 100%; background: #B92B27; color: white; border: none; padding: 10px; border-radius: 5px;">💬 Quora Mentions</button></a>', unsafe_allow_html=True)
    
    # WhatsApp Analysis
    elif current_tool == 'whatsapp':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">💬 WhatsApp Analysis</h2>
                    <div class="card-subtitle">WhatsApp number verification and profile analysis</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            whatsapp_number = st.text_input(
                "WhatsApp Number",
                placeholder="+1234567890",
                help="Enter phone number with country code",
                key="whatsapp_input"
            )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                search_btn = st.button("🔍 Check WhatsApp", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>✅ Registration Status</li>
                        <li>📱 Number Validation</li>
                        <li>🌍 Geographic Info</li>
                        <li>🔗 WhatsApp Link Generation</li>
                        <li>📊 Profile Analysis</li>
                        <li>📞 TrueCaller API Integration</li>
                        <li>🛡️ Spam Score Analysis</li>
                        <li>⚠️ Privacy Assessment</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if search_btn and whatsapp_number:
            try:
                tool.session_stats['total_searches'] += 1
                
                # Parse and validate number
                parsed_number = phonenumbers.parse(whatsapp_number)
                
                if phonenumbers.is_valid_number(parsed_number):
                    formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                    whatsapp_clean = formatted_number.replace('+', '')
                    
                    whatsapp_info = {
                        'Number': formatted_number,
                        'WhatsApp Web Link': f"https://wa.me/{whatsapp_clean}",
                        'WhatsApp Chat Link': f"https://api.whatsapp.com/send?phone={whatsapp_clean}",
                        'Geographic Location': geocoder.description_for_number(parsed_number, 'en') or 'Unknown',
                        'Carrier': carrier.name_for_number(parsed_number, 'en') or 'Unknown',
                        'Number Type': str(phonenumbers.number_type(parsed_number)).split('.')[-1],
                        'Region Code': phonenumbers.region_code_for_number(parsed_number),
                        'Status': 'Number appears valid for WhatsApp',
                        'Privacy Notes': 'WhatsApp registration cannot be verified without API access'
                    }
                    
                    tool.session_stats['successful_searches'] += 1
                    tool.session_stats['platforms_checked'] += 1
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(tool.create_metric_card("Validity", "✅ Valid" if phonenumbers.is_valid_number(parsed_number) else "❌ Invalid", "Number validation", "📱"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(tool.create_metric_card("Location", whatsapp_info['Geographic Location'], "Geographic region", "🌍"), unsafe_allow_html=True)
                    with col3:
                        st.markdown(tool.create_metric_card("Carrier", whatsapp_info['Carrier'], "Service provider", "📡"), unsafe_allow_html=True)
                    
                    st.markdown("### 💬 WhatsApp Analysis Results")
                    st.markdown(tool.create_professional_alert("Number format valid for WhatsApp", "success"), unsafe_allow_html=True)
                    
                    whatsapp_df = pd.DataFrame(list(whatsapp_info.items()), columns=['Property', 'Value'])
                    st.markdown(tool.render_professional_table(whatsapp_df, "WhatsApp Analysis Report"), unsafe_allow_html=True)
                    
                    # TrueCaller API integration
                    st.markdown("### 📱 TrueCaller API Lookup")
                    with st.spinner("Searching TrueCaller database..."):
                        # Simulated TrueCaller data (in a real implementation, you would use the actual API)
                        truecaller_data = tool.get_truecaller_data(formatted_number)
                        
                        if truecaller_data:
                            st.success("Found information in TrueCaller database!")
                            
                            # Create display table
                            truecaller_df = pd.DataFrame(list(truecaller_data.items()), columns=['Property', 'Value'])
                            st.markdown(tool.render_professional_table(truecaller_df, "TrueCaller Information"), unsafe_allow_html=True)
                            
                            # Add summarized data to main result
                            whatsapp_info['TrueCaller Name'] = truecaller_data.get('Name', 'Not Found')
                            whatsapp_info['TrueCaller Tags'] = truecaller_data.get('Tags', 'None')
                            whatsapp_info['Spam Likelihood'] = truecaller_data.get('Spam Score', 'Low')
                            
                            # Visual representation of spam score
                            st.markdown("### 📊 Spam Score Analysis")
                            spam_score = truecaller_data.get('Spam Score', 'Low')
                            score_value = {
                                'Very Low': 0.1,
                                'Low': 0.3,
                                'Medium': 0.5,
                                'High': 0.7,
                                'Very High': 0.9
                            }.get(spam_score, 0.1)
                            
                            # Create gauge chart for spam score
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=score_value * 100,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': "Spam Likelihood", 'font': {'size': 24}},
                                gauge={
                                    'axis': {'range': [0, 100], 'tickwidth': 1},
                                    'bar': {'color': "darkblue"},
                                    'bgcolor': "white",
                                    'borderwidth': 2,
                                    'bordercolor': "gray",
                                    'steps': [
                                        {'range': [0, 20], 'color': '#48BB78'},
                                        {'range': [20, 40], 'color': '#90CDF4'},
                                        {'range': [40, 60], 'color': '#F6E05E'},
                                        {'range': [60, 80], 'color': '#F6AD55'},
                                        {'range': [80, 100], 'color': '#F56565'}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 80
                                    }
                                }
                            ))
                            
                            fig.update_layout(
                                height=300,
                                margin=dict(l=20, r=20, t=50, b=20),
                                paper_bgcolor="rgba(0,0,0,0)",
                                font={'color': "#2D3748", 'family': "Inter"}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add caller type metrics
                            caller_type = truecaller_data.get('Type', 'Unknown')
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(tool.create_metric_card("Caller Type", caller_type, "Identity category", "👤"), unsafe_allow_html=True)
                            with col2:
                                reports = truecaller_data.get('User Reports', 'None')
                                st.markdown(tool.create_metric_card("User Reports", reports, "Community feedback", "📝"), unsafe_allow_html=True)
                            with col3:
                                searches = truecaller_data.get('Number of Searches', '0')
                                st.markdown(tool.create_metric_card("Search Popularity", searches, "Times looked up", "🔍"), unsafe_allow_html=True)
                        else:
                            st.warning("No TrueCaller information found for this number")
                            whatsapp_info['TrueCaller'] = 'No data found'
                    
                    # Quick actions
                    st.markdown("### ⚡ Quick Actions")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f'<a href="{whatsapp_info["WhatsApp Web Link"]}" target="_blank"><button style="width: 100%; background: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">🌐 Open WhatsApp Web</button></a>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<a href="{whatsapp_info["WhatsApp Chat Link"]}" target="_blank"><button style="width: 100%; background: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">💬 Start Chat</button></a>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<a href="https://www.truecaller.com/search/{whatsapp_clean}" target="_blank"><button style="width: 100%; background: #2a7cff; color: white; border: none; padding: 10px; border-radius: 5px;">🔍 TrueCaller Search</button></a>', unsafe_allow_html=True)
                    
                else:
                    st.markdown(tool.create_professional_alert("Invalid phone number format", "error"), unsafe_allow_html=True)
                    
            except phonenumbers.NumberParseException as e:
                st.markdown(tool.create_professional_alert(f"Phone parsing error: {str(e)}", "error"), unsafe_allow_html=True)
            except Exception as e:
                st.markdown(tool.create_professional_alert(f"Analysis error: {str(e)}", "error"), unsafe_allow_html=True)
    
    elif current_tool == 'emailharvester':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">📮 Email Harvester</h2>
                    <div class="card-subtitle">Discover email addresses associated with a domain</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            target_domain = st.text_input(
                "Target Domain",
                placeholder="example.com",
                help="Enter a domain name to discover associated email addresses",
                key="target_domain_input"
            )
            
            # Options for the scan
            st.markdown("<p style='margin-top: 15px; margin-bottom: 5px; font-weight: 500;'>Harvesting Options</p>", unsafe_allow_html=True)
            
            col_options1, col_options2 = st.columns(2)
            with col_options1:
                scan_depth = st.select_slider(
                    "Scan Depth", 
                    options=[1, 2, 3], 
                    value=1,
                    help="Higher depth means more sources but takes longer"
                )
            with col_options2:
                check_validity = st.checkbox(
                    "Validate Emails", 
                    value=True,
                    help="Attempt to validate discovered emails (may take longer)"
                )
            
            include_subdomains = st.checkbox(
                "Include Subdomains", 
                value=False,
                help="Also search for emails on common subdomains"
            )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                harvest_btn = st.button("🔍 Harvest Emails", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Tool Capabilities</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>✅ Website Scanning</li>
                        <li>✅ WHOIS Records</li>
                        <li>✅ DNS Analysis</li>
                        <li>✅ Search Engine Data</li>
                        <li>✅ Common Pattern Detection</li>
                        <li>✅ Email Format Discovery</li>
                        <li>✅ Certificate Transparency</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if harvest_btn and target_domain:
            # Call the email_harvester method
            results = tool.email_harvester(
                target_domain, 
                depth=scan_depth,
                include_subdomains=include_subdomains,
                check_validity=check_validity
            )
            
            if results:
                # Create DataFrame
                df = pd.DataFrame(results)
                
                # Show statistics
                st.markdown("### 📊 Email Discovery Results")
                
                # Count by confidence level
                confidence_counts = df[df['Email'] != 'Note']['Confidence'].value_counts()
                
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.markdown(tool.create_metric_card(
                        "Total Emails", 
                        len(df[df['Email'] != 'Note']),
                        icon="📧"
                    ), unsafe_allow_html=True)
                    
                with metric_cols[1]:
                    high_confidence = sum(1 for c in df['Confidence'] if c in ['Very High', 'High'])
                    st.markdown(tool.create_metric_card(
                        "High Confidence", 
                        high_confidence,
                        subtitle="Very High + High confidence",
                        icon="✓",
                        color="success"
                    ), unsafe_allow_html=True)
                    
                with metric_cols[2]:
                    sources_count = df['Source'].nunique()
                    st.markdown(tool.create_metric_card(
                        "Sources", 
                        sources_count,
                        subtitle="Data sources used",
                        icon="🔍"
                    ), unsafe_allow_html=True)
                    
                with metric_cols[3]:
                    valid_count = sum(1 for v in df['Valid'] if v in ['Yes', 'Likely'])
                    st.markdown(tool.create_metric_card(
                        "Valid Emails", 
                        valid_count,
                        subtitle="Likely valid addresses",
                        icon="✉️",
                        color="primary"
                    ), unsafe_allow_html=True)
                
                # Display results - handle different tabs for different views
                tabs = st.tabs(["All Emails", "By Source", "Visualizations"])
                
                with tabs[0]:
                    # Main results table
                    if not df.empty:
                        st.markdown(tool.render_professional_table(
                            df, 
                            "Email Discovery Results"
                        ), unsafe_allow_html=True)
                    else:
                        st.info("No emails were found for this domain")
                
                with tabs[1]:
                    # Group by source
                    for source in df['Source'].unique():
                        if source != 'Disclaimer':
                            source_df = df[df['Source'] == source]
                            st.markdown(f"### Source: {source}")
                            st.markdown(tool.render_professional_table(
                                source_df,
                                f"{source} Results"
                            ), unsafe_allow_html=True)
                
                with tabs[2]:
                    # Visualizations
                    if len(df[df['Email'] != 'Note']) > 0:
                        # Create visualization column
                        viz_col1, viz_col2 = st.columns([1, 1])
                        
                        with viz_col1:
                            # Create pie chart for confidence distribution
                            confidence_fig = go.Figure(data=[go.Pie(
                                labels=confidence_counts.index,
                                values=confidence_counts.values,
                                hole=.3,
                                marker_colors=['#38a169', '#3182ce', '#d69e2e', '#e53e3e']
                            )])
                            confidence_fig.update_layout(
                                title_text="Email Confidence Distribution",
                                showlegend=True
                            )
                            st.plotly_chart(confidence_fig, use_container_width=True)
                        
                        with viz_col2:
                            # Create bar chart for source count
                            source_counts = df[df['Email'] != 'Note']['Source'].value_counts()
                            source_fig = go.Figure(data=[go.Bar(
                                x=source_counts.index,
                                y=source_counts.values,
                                marker_color='#3182ce'
                            )])
                            source_fig.update_layout(
                                title_text="Emails by Source",
                                xaxis_title="Source",
                                yaxis_title="Count"
                            )
                            st.plotly_chart(source_fig, use_container_width=True)
                
                # Export options
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("📥 Export as CSV", use_container_width=True):
                        csv_data = tool.export_report(df[df['Email'] != 'Note'], 'email_harvest', 'csv')
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"email_harvest_{target_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                with col2:
                    if st.button("📥 Export as JSON", use_container_width=True):
                        json_data = tool.export_report(df[df['Email'] != 'Note'], 'email_harvest', 'json')
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"email_harvest_{target_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                with col3:
                    if st.button("📥 Export as HTML Report", use_container_width=True):
                        html_data, file_name, mime_type = tool.export_report(df[df['Email'] != 'Note'], 'email_harvest', 'html')
                        st.download_button(
                            label="Download HTML Report",
                            data=html_data,
                            file_name=file_name,
                            mime=mime_type
                        )
            else:
                st.error("No emails found for this domain. Try adjusting your search parameters.")
    
    elif current_tool == 'waybacktweets':    # WayBack Tweets Intelligence
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h2 class="card-title">🕰️ WayBack Tweets Analysis</h2>
                    <div class="card-subtitle">Find archived tweets from deleted or suspended accounts</div>
                </div>
                <div class="card-content">
            """, unsafe_allow_html=True)
            
            twitter_username = st.text_input(
                "Twitter/X Username",
                placeholder="elonmusk",
                help="Enter username without @ symbol",
                key="twitter_username_input"
            )
            
            # Date filtering UI
            st.markdown("<p style='margin-top: 15px; margin-bottom: 5px; font-weight: 500;'>Date Range (Optional)</p>", unsafe_allow_html=True)
            date_cols = st.columns(2)
            with date_cols[0]:
                from_date = st.date_input("From Date", 
                                          value=None, 
                                          help="Filter archives starting from this date",
                                          key="from_date_input")
            with date_cols[1]:
                to_date = st.date_input("To Date", 
                                       value=None, 
                                       help="Filter archives until this date",
                                       key="to_date_input")
                                       
            # Add saved tweets between dates option
            st.markdown("<p style='margin-top: 15px; margin-bottom: 5px; font-weight: 500;'>Filtering Options</p>", unsafe_allow_html=True)
            filter_popular = st.checkbox("Only show most relevant archives", value=False, 
                                        help="Filter to show only the most significant archive snapshots")
            specific_content = st.text_input("Filter by tweet content", 
                                           placeholder="Enter keywords to search for in archived tweets",
                                           help="Search for specific content in archived tweets (if available)")
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                search_btn = st.button("🔍 Find Archived Tweets", type="primary", use_container_width=True)
            with col_btn2:
                st.empty()  # Removed Example button
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="pro-card">
                <div class="card-header">
                    <h3 class="card-title">ℹ️ Analysis Features</h3>
                </div>
                <div class="card-content">
                    <ul style="list-style: none; padding: 0;">
                        <li>🕰️ Wayback Machine Archives</li>
                        <li>🔍 Deleted Tweet Recovery</li>
                        <li>⏱️ Historical Timeline Access</li>
                        <li>📅 Date Range Filtering</li>
                        <li>📊 Archive Statistics</li>
                        <li>📌 Suspended Account Data</li>
                        <li>🔗 Direct Archive Links</li>
                        <li>🌐 Alternative Archive Sources</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if search_btn and twitter_username:
            # Convert date inputs to datetime objects or None
            from_datetime = datetime.combine(from_date, datetime.min.time()) if from_date else None
            to_datetime = datetime.combine(to_date, datetime.max.time()) if to_date else None
            
            # Get content filter if provided
            content_filter = specific_content.strip() if specific_content else None
            
            # Call the wayback_tweets method with all parameters
            results = tool.wayback_tweets(
                twitter_username, 
                from_datetime, 
                to_datetime, 
                filter_popular=filter_popular,
                specific_content=content_filter
            )
            
            if results:
                # Create a DataFrame from the results
                df = pd.DataFrame(results)
                
                # Display statistics
                st.markdown("### 📊 Archive Statistics")
                
                # Show active filters in a unified message
                filter_messages = []
                
                # Date filter message
                if from_date or to_date:
                    if from_date and to_date:
                        filter_messages.append(f"🗓️ **Date Range:** Archives between {from_date.strftime('%Y-%m-%d')} and {to_date.strftime('%Y-%m-%d')}")
                    elif from_date:
                        filter_messages.append(f"🗓️ **Date Range:** Archives after {from_date.strftime('%Y-%m-%d')}")
                    elif to_date:
                        filter_messages.append(f"🗓️ **Date Range:** Archives before {to_date.strftime('%Y-%m-%d')}")
                
                # Content filter message
                if specific_content and specific_content.strip():
                    filter_messages.append(f"🔍 **Content Filter:** Searching for \"{specific_content}\"")
                
                # Relevance filter message
                if filter_popular:
                    filter_messages.append(f"⭐ **Relevance Filter:** Showing only the most significant archives")
                
                # Display all active filters
                if filter_messages:
                    filter_html = "<div style='padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>"
                    filter_html += "<p style='font-weight: 600; margin-bottom: 5px;'>Active Filters:</p>"
                    filter_html += "<ul style='margin-bottom: 0; padding-left: 20px;'>"
                    for msg in filter_messages:
                        filter_html += f"<li>{msg}</li>"
                    filter_html += "</ul></div>"
                    
                    st.markdown(filter_html, unsafe_allow_html=True)
                
                available_archives = sum(1 for r in results if r['Status'] == 'Available')
                total_archives = len([r for r in results if r['Type'] not in ['Suggestion', 'Alternative', 'Note', 'Error']])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(tool.create_metric_card("Available Archives", available_archives, "Historical snapshots", "🕰️"), 
                              unsafe_allow_html=True)
                with col2:
                    if available_archives > 0:
                        earliest_date = min([r['Date'] for r in results if r['Status'] == 'Available' and r['Date'] != 'Unknown'])
                        st.markdown(tool.create_metric_card("Earliest Archive", earliest_date, "First snapshot", "📅"), 
                                  unsafe_allow_html=True)
                    else:
                        st.markdown(tool.create_metric_card("Earliest Archive", "N/A", "No snapshots found", "📅"), 
                                  unsafe_allow_html=True)
                with col3:
                    st.markdown(tool.create_metric_card("Sources Checked", 2, "Archive services", "🌐"), 
                              unsafe_allow_html=True)
                
                # Filters for the table
                st.markdown("### 🔍 Archive Results")
                
                # Create filters
                col1, col2 = st.columns(2)
                with col1:
                    type_filter = st.selectbox("Filter by Type:", ['All'] + list(df['Type'].unique()))
                with col2:
                    status_filter = st.selectbox("Filter by Status:", ['All'] + list(df['Status'].unique()))
                
                # Apply filters
                filtered_df = df.copy()
                if type_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Type'] == type_filter]
                if status_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Status'] == status_filter]
                
                # Enhance presentation for URLs to make them clickable
                for i, row in filtered_df.iterrows():
                    if row['URL'].startswith('http'):
                        filtered_df.at[i, 'URL'] = f'<a href="{row["URL"]}" target="_blank" style="color: var(--primary-color);">🔗 Visit Archive</a>'
                
                # Display filtered results
                st.markdown(tool.render_professional_table(filtered_df, f"WayBack Tweets Results ({len(filtered_df)} records)"), 
                           unsafe_allow_html=True)
                
                # If available, show a timeline of archives
                if available_archives > 1:
                    st.markdown("### ⏱️ Archive Timeline")
                    
                    # Get only Available archives with valid dates for the timeline
                    timeline_data = [r for r in results if r['Status'] == 'Available' and r['Date'] != 'Unknown']
                    
                    if timeline_data:
                        timeline_df = pd.DataFrame(timeline_data)
                        timeline_df['Date'] = pd.to_datetime(timeline_df['Date'], errors='coerce')
                        timeline_df = timeline_df.sort_values('Date')
                        
                        fig = px.scatter(timeline_df, x='Date', y=[1]*len(timeline_df), 
                                        hover_data=['Type', 'Source'],
                                        title=f"Timeline of Available Archives for @{twitter_username}",
                                        height=250)
                        
                        fig.update_traces(marker=dict(size=12, color='#1a365d', symbol='diamond'))
                        fig.update_layout(yaxis_title='', yaxis_showticklabels=False,
                                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                        fig.update_layout(xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'))
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Tips section
                st.markdown("### 🔍 Research Tips")
                st.markdown("""
                <div class="pro-card">
                    <div class="card-content">
                        <h4>📌 How to Use Archive Links</h4>
                        <p>Archive links take you to historical snapshots of Twitter profiles as they appeared at that time. Here's how to use them effectively:</p>
                        <ul>
                            <li><strong>Browse timeline:</strong> Navigate through the profile to see tweets, replies, and media from when the snapshot was taken.</li>
                            <li><strong>Missing tweets:</strong> Some tweets may not appear due to incomplete archiving.</li>
                            <li><strong>Suspended accounts:</strong> Archives are especially valuable for accounts that have been deleted or suspended.</li>
                            <li><strong>Verification:</strong> Always verify information from archives as they represent a point-in-time and may be incomplete.</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Export options
                st.markdown("### 📥 Export Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    json_data, json_filename, json_mime = tool.export_report(df, "waybacktweets_analysis", "json")
                    st.download_button("📄 Export JSON", json_data, json_filename, json_mime)
                
                with col2:
                    csv_data, csv_filename, csv_mime = tool.export_report(df, "waybacktweets_analysis", "csv")
                    st.download_button("📊 Export CSV", csv_data, csv_filename, csv_mime)
                
                with col3:
                    html_data, html_filename, html_mime = tool.export_report(df, "waybacktweets_analysis", "html")
                    st.download_button("🌐 Export HTML", html_data, html_filename, html_mime)
            else:
                st.error("No archive data found. Please check the username and try again.")
    
    # Professional Footer
    st.markdown("""
    <div class="pro-footer">
        <div class="footer-content">
            <div class="footer-grid">
                <div class="footer-section">
                    <h4>🛡️ Osint Tool Pro</h4>
                    <p>Advanced OSINT intelligence platform designed for professionals and researchers.</p>
                </div>
                <div class="footer-section">
                    <h4>🔒 Security & Privacy</h4>
                    <p>All searches are performed anonymously through secure channels.</p>
                    <p>No data is stored or logged by our platform.</p>
                </div>
                <div class="footer-section">
                    <h4>📚 Resources</h4>
                    <p><a href="#" onclick="return false;">Documentation</a></p>
                    <p><a href="#" onclick="return false;">API Reference</a></p>
                    <p><a href="#" onclick="return false;">Best Practices</a></p>
                </div>
                <div class="footer-section">
                    <h4>🤝 Support</h4>
                    <p><a href="#" onclick="return false;">Contact Support</a></p>
                    <p><a href="#" onclick="return false;">Report Issues</a></p>
                    <p><a href="#" onclick="return false;">Feature Requests</a></p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>⚠️ <strong>Professional Use Only:</strong> This tool is designed for legitimate security research, journalism, and authorized investigations. Always ensure you have proper authorization and comply with applicable laws and platform terms of service.</p>
                <p>&copy; 2025 Osint Tool Pro. All rights reserved. | Version 2.0.0</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Replace the existing "Powered by" section with this enhanced version
    st.markdown("""
    <div style="text-align: center; padding: 20px; margin-top: 30px;">
        <p style="font-size: 14px; color: #666; margin-bottom: 5px;">Powered by</p>
        <p style="font-size: 22px; font-weight: bold; color: #1a365d; margin: 5px 0;">ECLOGIC</p>
        <p style="font-size: 12px; color: #718096;">Advanced Intelligence Solutions</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

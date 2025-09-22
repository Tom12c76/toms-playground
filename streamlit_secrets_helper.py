"""
Streamlit Secrets Helper Module

This module provides utilities for accessing Streamlit secrets
and configuring API connections for the toms-playground project.
"""

import streamlit as st
from typing import Dict, Optional, Any

def get_google_api_key() -> Optional[str]:
    """
    Get Google Gemini API key from Streamlit secrets.
    
    Returns:
        str: API key if found and properly configured, None otherwise
    """
    try:
        if "google" in st.secrets and "api_key" in st.secrets["google"]:
            api_key = st.secrets["google"]["api_key"]
            if api_key and api_key.strip() != "your_google_gemini_api_key_here":
                return api_key.strip()
    except Exception:
        pass
    return None

def get_refinitiv_credentials() -> Optional[Dict[str, str]]:
    """
    Get Refinitiv Data API credentials from Streamlit secrets.
    
    Returns:
        dict: Credentials dictionary with app_key, username, password
        None: If credentials are not properly configured
    """
    try:
        if "refinitiv" in st.secrets:
            credentials = {
                "app_key": st.secrets["refinitiv"].get("app_key", "").strip(),
                "username": st.secrets["refinitiv"].get("username", "").strip(), 
                "password": st.secrets["refinitiv"].get("password", "").strip()
            }
            
            # Check if all required credentials are present
            if all(credentials.values()) and all(
                cred != f"your_refinitiv_{key}_here" 
                for key, cred in credentials.items()
            ):
                return credentials
    except Exception:
        pass
    return None

def get_refinitiv_rdp_credentials() -> Optional[Dict[str, str]]:
    """
    Get Refinitiv RDP (Refinitiv Data Platform) credentials from Streamlit secrets.
    
    Returns:
        dict: RDP credentials with client_id and client_secret
        None: If credentials are not properly configured
    """
    try:
        if "refinitiv" in st.secrets and "rdp" in st.secrets["refinitiv"]:
            rdp_creds = st.secrets["refinitiv"]["rdp"]
            credentials = {
                "client_id": rdp_creds.get("client_id", "").strip(),
                "client_secret": rdp_creds.get("client_secret", "").strip()
            }
            
            if all(credentials.values()) and all(
                cred != f"your_rdp_{key}_here" 
                for key, cred in credentials.items()
            ):
                return credentials
    except Exception:
        pass
    return None

def get_api_key(service: str, key_name: str = "api_key") -> Optional[str]:
    """
    Get API key for any service from Streamlit secrets.
    
    Args:
        service: Name of the service (e.g., 'other_apis')
        key_name: Name of the key within the service section
        
    Returns:
        str: API key if found, None otherwise
    """
    try:
        if service in st.secrets and key_name in st.secrets[service]:
            api_key = st.secrets[service][key_name]
            if api_key and api_key.strip():
                return api_key.strip()
    except Exception:
        pass
    return None

def check_secrets_status() -> Dict[str, bool]:
    """
    Check the status of all configured secrets.
    
    Returns:
        dict: Status of each service's secrets (True = configured, False = missing)
    """
    status = {}
    
    # Check Google API
    status['google_gemini'] = get_google_api_key() is not None
    
    # Check Refinitiv
    status['refinitiv_data'] = get_refinitiv_credentials() is not None
    status['refinitiv_rdp'] = get_refinitiv_rdp_credentials() is not None
    
    return status

def display_secrets_help():
    """
    Display help information about configuring secrets.
    """
    st.markdown("""
    ### 🔐 Configuring API Secrets
    
    To configure your API keys securely:
    
    1. **Edit the secrets file**: `.streamlit/secrets.toml`
    2. **Replace placeholder values** with your actual API keys
    3. **Save the file** - Streamlit will automatically reload
    
    #### Google Gemini API:
    ```toml
    [google]
    api_key = "AIzaSy..."
    ```
    
    #### Refinitiv Data API:
    ```toml
    [refinitiv]
    app_key = "your_app_key"
    username = "your_username" 
    password = "your_password"
    ```
    
    #### Refinitiv RDP:
    ```toml
    [refinitiv.rdp]
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    ```
    
    **⚠️ Security Note**: The `.streamlit/secrets.toml` file is excluded from git 
    to keep your API keys secure. Never commit API keys to version control!
    """)
import streamlit as st
import os
from dotenv import load_dotenv

# Load .env for local dev if present
load_dotenv()

def get_config(key, default=None):
    """
    Retrieve configuration from Streamlit Secrets (priority) or Environment Variables.
    Safe to call even if secrets.toml is missing (local dev).
    """
    # 1. Try Streamlit Secrets
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass # Expected locally if no secrets.toml
    except Exception:
        pass 
        
    # 2. Try Environment Variables
    return os.getenv(key, default)

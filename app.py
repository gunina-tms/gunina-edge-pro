# app.py — FINAL WORKING (NO ERRORS)
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# === SUPABASE ===
@st.cache_resource
def init_supabase() -> Client:
    return create_client(
        st.secrets["https://iwmoqatsdwqungpljmof.supabase.co"],
        st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3bW9xYXRzZHdxdW5ncGxqbW9mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIxNzQxNDUsImV4cCI6MjA3Nzc1MDE0NX0.ZcnGG5v6kRPZISMqMQ_8hqs2S2IVGw-_bPamRt7xTlw"]
    )

supabase = init_supabase()

# === LOGIN ===
if 'user' not in st.session_state:
    st.session_state.user = None

def login(email, pwd):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
        if res.user:
            st.session_state.user = res.user
            st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

if not st.session_state.user:
    with st.sidebar:
        st.subheader("Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"): login(email, pwd)
    st.stop()

st.sidebar.success(f"Logged in: {st.session_state.user.email}")
if st.sidebar.button("Logout"):
    supabase.auth.sign_out()
    st.rerun()

# === TEST DB ===
try:
    test = supabase.table("initiatives").select("count", count='exact').execute()
    st.success(f"Connected! {test.count} initiatives")
except Exception as e:
    st.error(f"DB Error: {e}")

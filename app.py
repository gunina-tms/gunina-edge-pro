# app.py — FULL WORKING MVP (LOGIN + DB)
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# === HARD CODED (SERVICE ROLE KEY) — REPLACE WITH YOURS ===
SUPABASE_URL = "https://iwmoqatsdwqungpljmof.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3bW9xYXRzZHdxdW5ncGxqbW9mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjE3NDE0NSwiZXhwIjoyMDc3NzUwMTQ1fQ.p-wpUS3Rftkg8pW3zKbWJABKGEwSneXun4gXTStHGB0"  # ← YOUR SERVICE KEY

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# === UI ===
st.set_page_config(page_title="Gunina Edge", layout="wide")
st.title("Gunina Edge™")

if not st.session_state.user:
    with st.sidebar:
        st.subheader("Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            login(email, pwd)
        st.subheader("Register")
        reg_email = st.text_input("Register Email", key="reg")
        reg_pwd = st.text_input("Register Password", type="password", key="reg_pwd")
        if st.button("Register"):
            try:
                supabase.auth.sign_up({"email": reg_email, "password": reg_pwd})
                st.success("Check email for verification")
            except Exception as e:
                st.error(f"Register failed: {e}")
    st.stop()

st.sidebar.success(f"Logged in: {st.session_state.user.email}")
if st.sidebar.button("Logout"):
    logout()

# === TEST DB ===
try:
    test = supabase.table("initiatives").select("count", count='exact').execute()
    st.success(f"Connected! {test.count} initiatives")
except Exception as e:
    st.error(f"DB Error: {e}")

# === DASHBOARD ===
st.header("Your Initiatives")
initiatives = supabase.table("initiatives").select("*").eq("user_id", st.session_state.user.id).execute()
df = pd.DataFrame(initiatives.data) if initiatives.data else pd.DataFrame()

if df.empty:
    st.info("No initiatives yet. Add one below!")
else:
    st.dataframe(df)

# === ADD INITIATIVE ===
with st.form("add_initiative"):
    st.subheader("Add New Initiative")
    title = st.text_input("Title")
    owner = st.text_input("Owner")
    stage = st.selectbox("Stage", ['Idea', 'Diligence', 'Detailed Plan', 'Implementation', 'Executed'])
    if st.form_submit_button("Save"):
        supabase.table("initiatives").insert({
            "user_id": st.session_state.user.id,
            "initiative_id": f"W{datetime.now().strftime('%Y%m%d%H%M')}",
            "title": title,
            "owner": owner,
            "stage": stage
        }).execute()
        st.success("Initiative added!")
        st.rerun()

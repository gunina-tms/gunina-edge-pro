# app.py — GUNINA EDGE ENTERPRISE (Login + Multi-P&L + Live Edit)
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# === SUPABASE CLIENT ===
@st.cache_resource
def init_supabase() -> Client:
    return create_client(st.secrets["supabase"][" https://iwmoqatsdwqungpljmof.supabase.co"], st.secrets["supabase"]["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3bW9xYXRzZHdxdW5ncGxqbW9mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIxNzQxNDUsImV4cCI6MjA3Nzc1MDE0NX0.ZcnGG5v6kRPZISMqMQ_8hqs2S2IVGw-_bPamRt7xTlw"])

supabase = init_supabase()

# === LOGIN ===
if 'user' not in st.session_state:
    st.session_state.user = None

def login(email: str, password: str):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if res.user:
        st.session_state.user = res.user
        st.rerun()

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

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
            supabase.auth.sign_up({"email": reg_email, "password": reg_pwd})
            st.success("Check email for verification")
    st.stop()

st.sidebar.write(f"Logged in as: {st.session_state.user.email}")
if st.sidebar.button("Logout"): logout()

# === LOAD USER DATA ===
user_id = st.session_state.user.id
initiatives = supabase.table("initiatives").select("*").eq("user_id", user_id).execute()
df = pd.DataFrame(initiatives.data) if initiatives.data else pd.DataFrame()

# === TABS ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", "📝 Initiative", "💰 Financials", "📅 Plan", "⚠️ Risks"
])

# 1. DASHBOARD
with tab1:
    total_target = df['target'].sum() if not df.empty else 0
    st.metric("Total Target ($M)", f"{total_target / 1000:,.1f}")
    st.metric("Realized ($M)", f"{df['realized'].sum() / 1000:,.1f}")
    fig = px.bar(df, x="title", y="target", color="stage")
    st.plotly_chart(fig)

# 2. INITIATIVE EDITOR
with tab2:
    if st.button("Add New Initiative"):
        supabase.table("initiatives").insert({
            "user_id": user_id,
            "initiative_id": f"W{datetime.now().strftime('%Y%m%d%H%M')}",
            "title": "New Initiative",
            "stage": "Idea"
        }).execute()
        st.rerun()
    selected = st.selectbox("Select Initiative", df['initiative_id'])
    init_data = df[df['initiative_id'] == selected].iloc[0]
    with st.form("init_form"):
        title = st.text_input("Title", init_data['title'])
        owner = st.text_input("Owner", init_data['owner'])
        sponsor = st.text_input("Sponsor", init_data['sponsor'])
        workstream = st.text_input("Workstream", init_data['workstream'])
        stage = st.selectbox("Stage", ['Idea', 'Diligence', 'Detailed Plan', 'Implementation', 'Executed'], index=['Idea', 'Diligence', 'Detailed Plan', 'Implementation', 'Executed'].index(init_data['stage']))
        objective = st.text_area("Objective", init_data['business_objective'])
        if st.form_submit_button("Save"):
            supabase.table("initiatives").update({
                "title": title, "owner": owner, "sponsor": sponsor, "workstream": workstream,
                "stage": stage, "business_objective": objective, "updated_at": datetime.now()
            }).eq("initiative_id", selected).execute()
            st.success("Saved!")

# 3. FINANCIALS (Multi-P&L Ramp)
with tab3:
    impacts = supabase.table("pl_impacts").select("*").eq("initiative_id", df[df['initiative_id'] == selected]['id'].values[0]).execute()
    impact_df = pd.DataFrame(impacts.data)
    edited_impacts = st.data_editor(impact_df, num_rows="dynamic", column_config={
        "pl_line_item": st.column_config.TextColumn("P&L Line"),
        "impact_type": st.column_config.SelectColumn("Type", options=["Savings", "Cost Increase"]),
        "monthly_impact": st.column_config.NumberColumn("Monthly ($)")
    })
    if st.button("Save Impacts"):
        for _, row in edited_impacts.iterrows():
            supabase.table("pl_impacts").upsert(row.to_dict()).execute()
        st.success("Impacts Saved!")

    # 24-Month Ramp
    ramp_data = supabase.table("pl_financial_ramp").select("*").eq("pl_impact_id", impact_df['id'].iloc[0]).execute()
    ramp_df = pd.DataFrame(ramp_data.data).fillna(0)
    edited_ramp = st.data_editor(ramp_df, num_rows="dynamic")
    if st.button("Save Ramp"):
        for _, row in edited_ramp.iterrows():
            supabase.table("pl_financial_ramp").upsert(row.to_dict()).execute()
        st.success("Ramp Saved!")

# 4. PLAN (Milestones)
with tab4:
    milestones = supabase.table("milestones").select("*").eq("initiative_id", df[df['initiative_id'] == selected]['id'].values[0]).execute()
    milestone_df = pd.DataFrame(milestones.data)
    edited_milestones = st.data_editor(milestone_df, num_rows="dynamic")
    if st.button("Save Milestones"):
        for _, row in edited_milestones.iterrows():
            supabase.table("milestones").upsert(row.to_dict()).execute()
        st.success("Milestones Saved!")

# 5. RISKS
with tab5:
    risks = supabase.table("risks").select("*").eq("initiative_id", df[df['initiative_id'] == selected]['id'].values[0]).execute()
    risk_df = pd.DataFrame(risks.data)
    edited_risks = st.data_editor(risk_df, num_rows="dynamic")
    if st.button("Save Risks"):
        for _, row in edited_risks.iterrows():
            supabase.table("risks").upsert(row.to_dict()).execute()
        st.success("Risks Saved!")

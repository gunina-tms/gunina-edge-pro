import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gunina Edge Pro", layout="wide")
st.title("Gunina Edge Pro™ — M&A Command Center")
st.markdown("**Upload your 30+ initiative plan → Instant Gantt, S-curve, Risk, Financials**")

file = st.file_uploader("Upload Excel (.xlsx)", type=['xlsx'])
if file:
    df = pd.read_excel(file)

    tab1, tab2, tab3 = st.tabs(["📊 Gantt", "📈 S-Curve Ramp", "⚠️ Risk & Financials"])

    with tab1:
        fig = px.timeline(df, x_start="Start", x_end="End", y="Initiative", color="Workstream",
                          hover_data=["Owner", "Stage", "Risk", "% Complete"])
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_sorted = df.sort_values("End")
        df_sorted['Cum Target'] = df_sorted['Target ($M)'].cumsum()
        df_sorted['Cum Realized'] = df_sorted['Realized ($M)'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sorted['End'], y=df_sorted['Cum Target'], name="Target Ramp", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df_sorted['End'], y=df_sorted['Cum Realized'], name="Actual Ramp", line=dict(color="green", dash="dot")))
        fig.update_layout(title="Value Realization S-Curve", yaxis_title="$M")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Target", f"${df['Target ($M)'].sum():,.0f}M")
            st.metric("Total Gap", f"${(df['Target ($M)'] - df['Realized ($M)']).sum():,.0f}M")
            st.metric("High Risk", len(df[df['Risk'] == 'High']))
        with col2:
            fig = px.scatter(df, x='Target ($M)', y='% Complete', size='Risk Score', color='Workstream',
                             hover_data=['Initiative', 'Owner'])
            st.plotly_chart(fig, use_container_width=True)

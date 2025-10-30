{\rtf1\ansi\ansicpg1252\cocoartf2865
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import plotly.express as px\
import plotly.graph_objects as go\
\
st.set_page_config(page_title="Gunina Edge Pro", layout="wide")\
\
st.title("Gunina Edge Pro\'99 \'97 M&A Command Center")\
st.markdown("**Upload your 30+ initiative plan \uc0\u8594  Get Gantt, S-curve, Risk, Financials**")\
\
file = st.file_uploader("Upload Excel", type=['xlsx'])\
if file:\
    df = pd.read_excel(file)\
\
    tab1, tab2, tab3 = st.tabs(["Gantt", "S-Curve", "Risk & Financials"])\
\
    with tab1:\
        fig = px.timeline(df, x_start="Start", x_end="End", y="Initiative", color="Workstream")\
        fig.update_yaxes(autorange="reversed")\
        st.plotly_chart(fig, use_container_width=True)\
\
    with tab2:\
        df['Cum'] = df['Target ($M)'].cumsum()\
        fig = go.Figure()\
        fig.add_trace(go.Scatter(x=df['End'], y=df['Cum'], mode='lines+markers', name='Ramp'))\
        st.plotly_chart(fig)\
\
    with tab3:\
        col1, col2 = st.columns(2)\
        with col1:\
            st.metric("Total Target", f"$\{df['Target ($M)'].sum():,.0f\}M")\
            st.metric("At Risk", len(df[df['Risk']=='High']))\
        with col2:\
            fig = px.scatter(df, x='Target ($M)', y='Risk', size='% Complete', color='Workstream')\
            st.plotly_chart(fig)}
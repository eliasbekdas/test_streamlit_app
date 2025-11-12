import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Test App")
st.write("This is a test app for Streamlit WITH GITHUB.")

name = st.text_input("Hey what's your name?")

if name:
    st.success(f"Hi {name}, welcome to the app!")

st.balloons()
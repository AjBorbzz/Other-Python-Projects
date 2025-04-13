import streamlit as st
import json
import requests 

st.title("Extract PDF to Text")

st.write("")
st.divider()

uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

if st.button("Extract PDF"):
    res = requests.post(url = "http://127.0.0.1:8000/extract", data=json.dumps(uploaded_file))
    
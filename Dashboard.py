import streamlit as st
from PIL import Image

image = Image.open('pages/icons/logo.png')
st.image(image,width=100)

st.markdown("""


# AWS management console

This is an example project using [Streamlint](https://streamlit.io) framework and Python to create your own AWS Console.

Currently, it supports dynamic tables, export, and summarizing the total number of objects and their total size for S3 buckets.



""")
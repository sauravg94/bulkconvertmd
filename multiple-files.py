import streamlit as st
import pandas as pd
import requests
from markdownify import markdownify as md
from urllib.parse import urlparse
import os
import zipfile
import io
import time

st.set_page_config(page_title="Batch Helpx → Markdown Converter", layout="centered")
st.title("📄 Convert Helpx URLs to Markdown (Batch)")

uploaded_file = st.file_uploader("Upload a CSV file with one Helpx URL per row", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, header=None, names=["url"])
    urls = df["url"].dropna().tolist()

    if st.button("Convert and Download Markdown ZIP"):
        zip_buffer = io.BytesIO()
        total = len(urls)

        # Progress bar UI
        progress_bar = st.progress(0)
        status_text = st.empty()

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for i, url in enumerate(urls):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    html = response.text
                    markdown = md(html, heading_style="ATX")

                    path = urlparse(url).path
                    filename = path.strip("/").replace("/", "-") + ".md"
                    zipf.writestr(filename, markdown)

                    status_text.text(f"✅ Processed {i + 1}/{total}: {filename}")
                except Exception as e:
                    st.error(f"❌ Failed to process {url}: {e}")

                # Update progress bar
                progress_bar.progress((i + 1) / total)

        zip_buffer.seek(0)
        st.success(f"✅ Converted {total} pages to Markdown.")
        st.download_button(
            label="📥 Download Markdown ZIP",
            data=zip_buffer,
            file_name="helpx_markdown_files.zip",
            mime="application/zip"
        )

# app.py
import streamlit as st
from scraper import scrape_realstate
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Dubizzle Real Estate Scraper", layout="centered")

st.title("🏘️ Dubizzle Real Estate Scraper")
st.write("Scrape apartment listings from Dubizzle Egypt automatically.")

# 🔢 Number of listings input
num_ads = st.number_input("Number of Listings to Scrape", min_value=1, max_value=500, value=10, step=1)

# ▶️ Button to start scraping
if st.button("🔍 Start Scraping"):
    with st.spinner(f"Scraping {num_ads} listings from Dubizzle..."):
        csv_path = scrape_realstate(num_ads)
        df = pd.read_csv(csv_path)
        st.success("✅ Scraping completed!")
        st.dataframe(df)
        st.download_button("📥 Download CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=os.path.basename(csv_path), mime="text/csv")

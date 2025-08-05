import streamlit as st
import requests
import json
import pandas as pd

def process_and_display_batch(data, table_placeholder):
    """
    Convert the batch data into a DataFrame and display it in the Streamlit app.
    """
    # Convert to DataFrame
    df = pd.DataFrame(data["new_items"])
    
    # List of columns to show
    columns_to_show = ['Company', 'Industry', 'Street', 'City', 'Business_phone', 'Website']
    # Filter existing columns
    existing_columns = [col for col in columns_to_show if col in df.columns]

    # Use the placeholder to display the DataFrame
    table_placeholder.dataframe(df[existing_columns], use_container_width=True)

def run_scraper_realtime(industry: str, location: str):
    """
    Running the scraper in real-time and updating the Streamlit app with results.
    """
    status_placeholder = st.empty()
    table_placeholder = st.empty()

    API_URL = f"https://api.saasquatchleads.com/scraper/scrape-stream?industry={industry}&location={location}"
    
    try:
        response = requests.get(API_URL, stream=True, timeout=90)
        response.raise_for_status()
        
        done_info = None

        # Iterate over the response stream
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                if decoded_line.startswith("data:"):
                    try:
                        data = json.loads(decoded_line[5:].strip())
                        
                        # If "new_items" is in the data that means we have new results to display
                        if "new_items" in data:
                            total_scraped = data.get('total_scraped', 0)
                            status_placeholder.info(f"⏳ Receiving data... Total found: **{total_scraped}**")
                            process_and_display_batch(data, table_placeholder)
                        
                        # If completed
                        elif "message" in data and "Scraping completed" in data["message"]:
                            done_info = data
                    
                    #Invalid JSON handling        
                    except json.JSONDecodeError:
                        continue

        # After the loop, check if we have a done message
        if done_info:
            total_scraped = done_info.get('total_scraped', 'N/A')
            elapsed_time = done_info.get('elapsed_time', 0)
            status_placeholder.success(f"Search complete! Final total **{total_scraped}** results in **{elapsed_time:.2f}** seconds.")
        else:
            status_placeholder.warning("The search was completed but no confirmation message was received.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the API")


# --- Main View ---

st.set_page_config(page_title="Pencari Prospek", page_icon="📊", layout="wide")

st.title("Company Finder")
st.markdown("Find companies by industry and location.")

with st.form(key="search_form"):
    col1, col2 = st.columns(2)
    with col1:
        industry_input = st.text_input("Industry", placeholder="Enter Industry (e.g. mining, restaurant, hotel)")
    with col2:
        location_input = st.text_input("Location", placeholder="Enter Location (e.g. Sudbury, MA, USA)")
    
    submit_button = st.form_submit_button(label="🚀 Find Companies")

if submit_button:
    if industry_input and location_input:
        run_scraper_realtime(industry_input, location_input)
    else:
        st.warning("Mohon isi kedua kolom industri dan lokasi.")
import streamlit as st
import requests
import json
import pandas as pd
import uuid
import hashlib

########## DUMMY SECTION ##########

def get_dummy_data():
    return {
        "batch": 1,
        "new_items": [
            {
                "Company": "AlphaTech Innovations",
                "Industry": "Technology",
                "Street": "123 Innovation Way",
                "City": "Jakarta",
                "Business_phone": "(021) 123-4567",
                "Website": "http://www.alphatech.co.id",
                "More": "View"
            },
            {
                "Company": "Bumi Hijau Organik",
                "Industry": "Agriculture",
                "Street": "88 Greenfield Rd",
                "City": "Bandung",
                "Business_phone": "(022) 765-4321",
                "Website": "http://www.bumihijau.com",
                "More": "View"
            },
            {
                "Company": "SmartEdu Nusantara",
                "Industry": "Education",
                "Street": "10 Learning Blvd",
                "City": "Surabaya",
                "Business_phone": "(031) 789-0123",
                "Website": "http://www.smartedu.id",
                "More": "View"
            },
            {
                "Company": "Medika Sehat",
                "Industry": "Healthcare",
                "Street": "56 Wellness Street",
                "City": "Yogyakarta",
                "Business_phone": "(0274) 321-8765",
                "Website": "http://www.medikasehat.co.id",
                "More": "View"
            },
            {
                "Company": "EcoTrans Logistik",
                "Industry": "Transportation",
                "Street": "22 Mobility Ave",
                "City": "Semarang",
                "Business_phone": "(024) 654-7890",
                "Website": "http://www.ecotrans.co.id",
                "More": "View"
            }
        ]
    }
    
def run_scraper_realtime_dummy(industry: str, location: str):
    """
    Dummy version: Load and display static dummy data instead of real-time API.
    """
    status_placeholder = st.empty()
    table_placeholder = st.empty()
    batch_count = 1

    # Langsung ambil dummy data
    data = get_dummy_data()

    # Simpan data ke session state SEBELUM menampilkan
    st.session_state['search_results'] = data
    st.session_state['has_search_results'] = True

    # Tampilkan status dan data
    total_scraped = len(data["new_items"])
    status_placeholder.info(f"📦 Showing dummy data... Total found: **{total_scraped}**")
    process_and_display_batch(data, table_placeholder, batch_count)

    status_placeholder.success("✅ Dummy data loaded successfully.")
    
########## END OF DUMMY SECTION ##########

def process_and_display_batch(data, table_placeholder, batch_count):
    df = pd.DataFrame(data["new_items"])
    columns_to_show = ['Company', 'Industry', 'Street', 'City', 'Business_phone', 'Website']
    existing_columns = [col for col in columns_to_show if col in df.columns]

    with table_placeholder.container():
        header_cols = st.columns(len(existing_columns) + 1)
        for idx, col_name in enumerate(existing_columns):
            header_cols[idx].markdown(f"**{col_name}**")
        header_cols[-1].markdown("**Action**")

        for i, row in df.iterrows():
            row_cols = st.columns(len(existing_columns) + 1)
            for idx, col_name in enumerate(existing_columns):
                row_cols[idx].write(row[col_name])
                
            company = row["Company"]
            button_key = f"detail_btn_{i}_{batch_count}_{hash(company) % 10000}"
            
            # Check if this specific button was clicked
            if row_cols[-1].button("More", key=button_key):
                # Store the selected company data in session state
                st.session_state['selected_company'] = row.to_dict()
                st.session_state['detail_data'] = data
                # Change to detail page
                try:
                    st.switch_page("pages/detail_data.py")
                except Exception as e:
                    st.error(f"Could not navigate to detail page: {e}")

def run_scraper_realtime(industry: str, location: str):
    """
    Running the scraper in real-time and updating the Streamlit app with results.
    """
    status_placeholder = st.empty()
    table_placeholder = st.empty()
    batch_count = 0

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
                            batch_count += 1
                            total_scraped = data.get('total_scraped', 0)
                            status_placeholder.info(f"⏳ Receiving data... Total found: **{total_scraped}**")
                            
                            # Store results in session state
                            st.session_state['search_results'] = data
                            st.session_state['has_search_results'] = True
                            
                            process_and_display_batch(data, table_placeholder, batch_count)
                        
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

st.set_page_config(page_title="Pencari Prospek", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
if 'has_search_results' not in st.session_state:
    st.session_state['has_search_results'] = False

# Main page content
st.title("Company Finder")
st.markdown("Find companies by industry and location.")

# Search form
with st.form(key="search_form"):
    col1, col2 = st.columns(2)
    with col1:
        industry_input = st.text_input("Industry", placeholder="Enter Industry (e.g. mining, restaurant, hotel)")
    with col2:
        location_input = st.text_input("Location", placeholder="Enter Location (e.g. Sudbury, MA, USA)")
    
    submit_button = st.form_submit_button(label="🚀 Find Companies")

# Handle search form submission
if submit_button:
    if industry_input and location_input:
        run_scraper_realtime(industry_input, location_input)
    else:
        st.warning("Mohon isi kedua kolom industri dan lokasi.")

# If we have previous search results, show them
elif st.session_state.get('has_search_results', False) and 'search_results' in st.session_state:
    st.info("📋 Showing previous search results:")
    process_and_display_batch(st.session_state['search_results'], st.container(), 1)
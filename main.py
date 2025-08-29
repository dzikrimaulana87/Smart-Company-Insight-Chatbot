import streamlit as st
import requests
import json
import pandas as pd
import uuid
import hashlib

def process_and_display_batch(data, table_placeholder, batch_count):
    """Process and display batch data with proper error handling"""
    try:
        # Validate data structure
        if not isinstance(data, dict) or "new_items" not in data:
            st.error("Invalid data format received")
            return
        
        # Check if new_items is empty or not a list
        if not data["new_items"] or not isinstance(data["new_items"], list):
            st.warning("No new items to display")
            return
            
        df = pd.DataFrame(data["new_items"])
        
        # Define columns and check if they exist
        columns_to_show = ['Company', 'Industry', 'Street', 'City', 'Business_phone', 'Website']
        existing_columns = [col for col in columns_to_show if col in df.columns]
        
        # If no columns match, show all available columns
        if not existing_columns:
            existing_columns = list(df.columns)
            st.warning(f"Expected columns not found. Showing available columns: {existing_columns}")

        with table_placeholder.container():
            # Create header
            header_cols = st.columns(len(existing_columns) + 1)
            for idx, col_name in enumerate(existing_columns):
                header_cols[idx].markdown(f"**{col_name}**")
            header_cols[-1].markdown("**Action**")

            # Display data rows
            for i, row in df.iterrows():
                row_cols = st.columns(len(existing_columns) + 1)
                
                # Display each column value
                for idx, col_name in enumerate(existing_columns):
                    # Handle missing values gracefully
                    value = row.get(col_name, "N/A")
                    row_cols[idx].write(str(value))
                
                # Generate unique button key
                company_name = str(row.get("Company", f"company_{i}"))
                button_key = f"detail_btn_{i}_{batch_count}_{abs(hash(company_name)) % 10000}"
                
                # Detail button with error handling
                if row_cols[-1].button("More", key=button_key):
                    # Store the selected company data in session state
                    st.session_state['selected_company'] = row.to_dict()
                    st.session_state['detail_data'] = data
                    
                    # Try to navigate to detail page
                    try:
                        st.switch_page("pages/detail_data.py")
                    except FileNotFoundError:
                        st.error("Detail page not found. Please ensure 'pages/detail_data.py' exists.")
                    except Exception as e:
                        st.error(f"Could not navigate to detail page: {e}")
                        
    except Exception as e:
        st.error(f"Error processing batch data: {e}")

def run_scraper_realtime(industry: str, location: str):
    """
    Running the scraper in real-time and updating the Streamlit app with results.
    """
    status_placeholder = st.empty()
    table_placeholder = st.empty()
    batch_count = 0

    # URL encode parameters to handle special characters
    import urllib.parse
    encoded_industry = urllib.parse.quote(industry)
    encoded_location = urllib.parse.quote(location)
    API_URL = f"https://api.saasquatchleads.com/scraper/scrape-stream?industry={encoded_industry}&location={encoded_location}"
    
    try:
        status_placeholder.info("🔍 Starting search...")
        
        # Make request with proper headers
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
        }
        
        response = requests.get(API_URL, stream=True, timeout=90, headers=headers)
        response.raise_for_status()
        
        done_info = None
        has_received_data = False

        # Iterate over the response stream
        for line in response.iter_lines(decode_unicode=True):
            if line and line.strip():  # Check for non-empty lines
                try:
                    # Handle Server-Sent Events format
                    if line.startswith("data:"):
                        json_data = line[5:].strip()
                        
                        # Skip empty data lines
                        if not json_data:
                            continue
                            
                        data = json.loads(json_data)
                        
                        # If "new_items" is in the data that means we have new results to display
                        if "new_items" in data:
                            batch_count += 1
                            has_received_data = True
                            total_scraped = data.get('total_scraped', 0)
                            status_placeholder.info(f"⏳ Receiving data... Total found: **{total_scraped}**")
                            
                            # Store results in session state
                            st.session_state['search_results'] = data
                            st.session_state['has_search_results'] = True
                            
                            process_and_display_batch(data, table_placeholder, batch_count)
                        
                        # If completed
                        elif "message" in data and "Scraping completed" in data["message"]:
                            done_info = data
                            
                    # Handle other SSE event types if needed
                    elif line.startswith("event:") or line.startswith("id:"):
                        continue
                    
                except json.JSONDecodeError as e:
                    # Log JSON errors but continue processing
                    st.warning(f"Received invalid JSON data: {line[:100]}...")
                    continue
                except Exception as e:
                    st.error(f"Error processing line: {e}")
                    continue

        # After the loop, check if we have a done message
        if done_info:
            total_scraped = done_info.get('total_scraped', 'N/A')
            elapsed_time = done_info.get('elapsed_time', 0)
            status_placeholder.success(f"✅ Search complete! Final total **{total_scraped}** results in **{elapsed_time:.2f}** seconds.")
        elif has_received_data:
            status_placeholder.info("Search completed successfully!")
        else:
            status_placeholder.warning("No data was received from the search.")

    except requests.exceptions.Timeout:
        status_placeholder.error("⏰ Request timed out. Please try again with a more specific search.")
    except requests.exceptions.ConnectionError:
        status_placeholder.error("🌐 Connection error. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        status_placeholder.error(f"🚫 API returned error: {e}")
    except requests.exceptions.RequestException as e:
        status_placeholder.error(f"❌ Failed to connect to the API: {e}")
    except Exception as e:
        status_placeholder.error(f"❌ Unexpected error: {e}")

# --- Main View ---

st.set_page_config(
    page_title="Prospect Finder", 
    page_icon="📊", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'has_search_results' not in st.session_state:
    st.session_state['has_search_results'] = False
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None
if 'selected_company' not in st.session_state:
    st.session_state['selected_company'] = None

# Main page content
st.title("🏢 Company Finder")
st.markdown("Find companies by industry and location using real-time data.")

# Search form
with st.form(key="search_form"):
    col1, col2 = st.columns(2)
    with col1:
        industry_input = st.text_input(
            "Industry", 
            placeholder="e.g., mining, restaurant, hotel",
            help="Enter the industry you want to search for"
        )
    with col2:
        location_input = st.text_input(
            "Location", 
            placeholder="e.g., Sudbury, MA, USA",
            help="Enter the location (city, state, country)"
        )
    
    submit_button = st.form_submit_button(label="🚀 Find Companies", type="primary")

# Handle search form submission
if submit_button:
    if industry_input.strip() and location_input.strip():
        # Clear previous results
        st.session_state['has_search_results'] = False
        st.session_state['search_results'] = None
        
        # Run the search
        run_scraper_realtime(industry_input.strip(), location_input.strip())
    else:
        st.warning("⚠️ Please fill in both industry and location fields.")

# If we have previous search results, show them
elif st.session_state.get('has_search_results', False) and st.session_state.get('search_results'):
    st.info("📋 Showing previous search results:")
    try:
        process_and_display_batch(st.session_state['search_results'], st.container(), 1)
    except Exception as e:
        st.error(f"Error displaying previous results: {e}")
        # Clear corrupted results
        st.session_state['has_search_results'] = False
        st.session_state['search_results'] = None
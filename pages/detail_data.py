import streamlit as st

def show_company_details():
    """Display detailed view of selected company"""
    if 'selected_company' in st.session_state:
        company = st.session_state['selected_company']
        
        st.subheader(f"Details for {company['Company']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Industry:** {company.get('Industry', 'N/A')}")
            st.write(f"**Phone:** {company.get('Business_phone', 'N/A')}")
            st.write(f"**Website:** {company.get('Website', 'N/A')}")
        
        with col2:
            st.write(f"**Street:** {company.get('Street', 'N/A')}")
            st.write(f"**City:** {company.get('City', 'N/A')}")
        
        if st.button("← Back to Search Results"):
            del st.session_state['selected_company']
            st.switch_page("main.py")
            
if 'selected_company' in st.session_state:
    st.title("Company Details")
    show_company_details()
else:
    st.error("No company selected. Please go back to the search results.")
    if st.button("← Back to Search Results"):
        st.switch_page("main.py")
    

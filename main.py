import streamlit as st
import pandas as pd
from streamlit_markmap import markmap
import io
import json

# Set page config at the very beginning
st.set_page_config(layout="wide", page_title="URL Taxonomy Visualizer")

@st.cache_data
def load_data(uploaded_file):
    try:
        data = pd.read_excel(uploaded_file)
        data = data.drop_duplicates(subset=['Full URL'])
        st.success(f"Data loaded successfully. Shape after removing duplicates: {data.shape}")
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")
        st.stop()

def process_data(data):
    hierarchy = {"name": "URL Hierarchy", "children": []}
    for _, row in data.iterrows():
        current = hierarchy
        for i in range(8):
            if pd.notna(row[f'L{i}']):
                category = str(row[f'L{i}'])
                child = next((c for c in current['children'] if c['name'] == category), None)
                if child is None:
                    child = {"name": category, "children": []}
                    current['children'].append(child)
                current = child
            else:
                break
        if 'urls' not in current:
            current['urls'] = []
        current['urls'].append(row['Full URL'])
    return hierarchy

def count_items(node):
    if 'children' in node:
        count = sum(count_items(child) for child in node['children'])
        if 'urls' in node:
            count += len(node['urls'])
        node['name'] = f"{node['name']} ({count})"
        return count
    return 1

# Streamlit UI
st.title("Hierarchical Visualization of URLs with Counts and Colors")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

# Download sample template
def get_sample_template():
    df = pd.DataFrame({
        'Full URL': ['https://example.com/page1', 'https://example.com/page2'],
        'L0': ['Category1', 'Category2'],
        'L1': ['Subcategory1', 'Subcategory2'],
        'L2': ['Subsubcategory1', 'Subsubcategory2'],
    })
    for i in range(3, 8):
        df[f'L{i}'] = ''
    return df

if st.button('Download Sample Template'):
    sample_df = get_sample_template()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Sheet1')
    buffer.seek(0)
    st.download_button(
        label="Click here to download the sample template",
        data=buffer,
        file_name="sample_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    # Process data into a hierarchical structure
    hierarchy = process_data(data)
    
    # Count items and update node names
    count_items(hierarchy)

    # Convert hierarchy to JSON string
    markmap_content = json.dumps(hierarchy)

    # CSS to control the size of the markmap
    st.markdown("""
        <style>
        .stMarkmap > div {
            height: 600px;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render the markmap
    markmap(markmap_content)

    # Provide user interaction for opening URLs
    st.markdown("""
    ### Click on the URLs below to navigate
    """)
    selected_url = st.selectbox('Select URL to open', sorted(data['Full URL'].unique()))
    if st.button('Open URL'):
        st.write(f"Opening URL: {selected_url}")
        st.markdown(f'<a href="{selected_url}" target="_blank">Click here to open the URL</a>', unsafe_allow_html=True)
else:
    st.info("Please upload an Excel file to visualize the URL hierarchy.")

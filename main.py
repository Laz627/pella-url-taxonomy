import streamlit as st
import pandas as pd
from streamlit_markmap import markmap
import io
import time

# Set page config at the very beginning
st.set_page_config(layout="wide", page_title="URL Taxonomy Visualizer")

# App Title and Credits
st.title("URL Taxonomy Visualizer")
st.markdown("**Created by Brandon Lazovic**")

# Instructions for Using the Template
st.markdown("""
### Instructions for Using the Template
1. Download the sample template provided below.
2. Fill in your data, ensuring the following columns are included:
   - `Full URL`: The full URL of the page.
   - `L0` to `L7`: Hierarchical categories for the URL (e.g., Category, Subcategory, etc.).
3. Upload the filled template using the file uploader below.
4. The visualization will automatically generate based on the uploaded data.

*Note*: Make sure to maintain the column headers and fill in each level as needed. Leave cells empty if the URL does not go deeper in the hierarchy.
""")

def load_data(uploaded_file):
    """
    Loads data from an uploaded file and removes duplicates based on 'Full URL' column.
    """
    try:
        data = pd.read_excel(uploaded_file)
        data = data.drop_duplicates(subset=['Full URL'])
        st.success(f"Data loaded successfully. Shape after removing duplicates: {data.shape}")
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")
        st.stop()

def add_to_tree(tree, path, url):
    """
    Adds a URL to the hierarchical tree based on its path.
    """
    current = tree
    for component in path:
        if component not in current:
            current[component] = {'_urls': [], '_count': 0}
        current = current[component]
        current['_count'] += 1
    current['_urls'].append(url)

def create_markmap_content(tree, level=0):
    """
    Creates a markdown content string suitable for markmap rendering.
    """
    content = ""
    for key, value in sorted(tree.items()):
        if key not in ['_urls', '_count']:
            url_count = value['_count']
            content += f"{'  ' * level}- {key} ({url_count})\n"
            content += create_markmap_content(value, level + 1)
            # Add URLs as the final nodes
            if '_urls' in value and value['_urls']:
                content += f"{'  ' * (level + 1)}- URLs\n"
                for url in sorted(value['_urls']):
                    content += f"{'  ' * (level + 2)}- {url}\n"
    return content

def process_data(data):
    """
    Processes the data to create a hierarchical tree structure.
    """
    category_tree = {}
    problematic_urls = []
    for _, row in data.iterrows():
        url = row['Full URL']
        category_path = [str(row[f'L{i}']) for i in range(8) if pd.notna(row[f'L{i}'])]
        if not category_path:
            problematic_urls.append(url)
            continue
        add_to_tree(category_tree, category_path, url)
    
    if problematic_urls:
        st.warning("The following URLs couldn't be properly categorized:")
        st.write(problematic_urls)
    
    return category_tree

def get_sample_template():
    """
    Generates a sample DataFrame for user download.
    """
    df = pd.DataFrame({
        'Full URL': ['https://example.com/page1', 'https://example.com/page2'],
        'L0': ['Category1', 'Category2'],
        'L1': ['Subcategory1', 'Subcategory2'],
        'L2': ['Subsubcategory1', 'Subsubcategory2'],
        'L3': ['Subsubsubcategory1', 'Subsubsubcategory2'],
    })
    for i in range(4, 8):
        df[f'L{i}'] = ''
    return df

# Streamlit UI for File Upload
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

# Download sample template
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

    # Display progress bar while processing data
    progress_bar = st.progress(0)
    for i in range(1, 101):
        time.sleep(0.01)
        progress_bar.progress(i)

    # Process data into a tree structure based on the category columns
    category_tree = process_data(data)

    # Create markmap content
    markmap_content = f"""
---
markmap:
  initialExpandLevel: 2  # Ensures only up to the 2nd level nodes are expanded by default
  colorFreezeLevel: 3  # Keeps the color consistent from the third level onward
---
# URL Hierarchy
{create_markmap_content(category_tree)}
"""

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

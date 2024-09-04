import streamlit as st
import pandas as pd
from streamlit_markmap import markmap

# Set page config at the very beginning
st.set_page_config(layout="wide", page_title="URL Taxonomy Visualizer")

def load_data(uploaded_file):
    try:
        data = pd.read_excel(uploaded_file)
        data = data.drop_duplicates(subset=['Full URL'])
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")
        st.stop()

def add_to_tree(tree, path, url):
    current = tree
    for component in path:
        if component not in current:
            current[component] = {'_urls': [], '_count': 0}
        current = current[component]
        current['_count'] += 1
    current['_urls'].append(url)

def create_markmap_content(tree, level=0):
    content = ""
    for key, value in sorted(tree.items()):
        if key not in ['_urls', '_count']:
            url_count = value['_count']
            content += f"{'  ' * level}- {key} ({url_count})\n"
            if '_urls' in value and value['_urls']:
                content += f"{'  ' * (level + 1)}- URLs\n"
                for url in sorted(value['_urls']):
                    content += f"{'  ' * (level + 2)}- [{url}]({url})\n"
            content += create_markmap_content(value, level + 1)
    return content

def process_data(data):
    category_tree = {}
    problematic_urls = []
    for _, row in data.iterrows():
        url = row['Full URL']
        category_path = [str(row[col]) for col in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'] if pd.notna(row[col])]
        if not category_path:
            problematic_urls.append(url)
            continue
        add_to_tree(category_tree, category_path, url)
    
    if problematic_urls:
        st.warning("The following URLs couldn't be properly categorized:")
        st.write(problematic_urls)
    
    return category_tree

# Streamlit UI
st.title("Hierarchical Visualization of URLs with Counts and Colors")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)
    st.success(f"Data loaded successfully. Shape after removing duplicates: {data.shape}")

    # Process data into a tree structure based on the category columns
    category_tree = process_data(data)

    # Create markmap content
    markmap_content = """
    ---
    markmap:
      colorFreezeLevel: 2
      color: '#1f77b4'
      initialExpandLevel: 2
      maxWidth: 300
    ---
    # URL Hierarchy
    """ + create_markmap_content(category_tree)

    # CSS to control the size of the markmap and hide URLs
    st.markdown("""
        <style>
        .stMarkmap > div {
            height: 600px;
            width: 100%;
        }
        .markmap-node-text:not(:hover) a {
            color: transparent;
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

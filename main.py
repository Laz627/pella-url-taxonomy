import streamlit as st
import pandas as pd
from streamlit_markmap import markmap
from io import BytesIO

# Set page config at the very beginning
st.set_page_config(layout="wide", page_title="URL Taxonomy Visualizer")

def load_data(file):
    try:
        data = pd.read_excel(file)
        data = data.drop_duplicates(subset=['Full URL'])
        st.success(f"Data loaded successfully. Shape after removing duplicates: {data.shape}")
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")
        return None

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
                    content += f"{'  ' * (level + 2)}- {url}\n"
            content += create_markmap_content(value, level + 1)
    return content

def process_data(data):
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

def create_template_example():
    # Sample DataFrame for template
    template_data = {
        'Full URL': ['http://example.com/page1', 'http://example.com/page2'],
        'L1': ['Category1', 'Category1'],
        'L2': ['Subcategory1', 'Subcategory2'],
        'L3': [None, 'Subcategory2.1'],
        'L4': [None, None],
        'L5': [None, None],
        'L6': [None, None],
        'L7': [None, None],
        'L8': [None, None]
    }
    template_df = pd.DataFrame(template_data)
    
    # Convert DataFrame to Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        template_df.to_excel(writer, index=False)
    output.seek(0)
    
    return output

# UI for downloading template and uploading data
st.sidebar.markdown("## Download Template Example")
st.sidebar.download_button(
    label="Download Excel Template",
    data=create_template_example(),
    file_name="URL_Taxonomy_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xls", "xlsx"])

if uploaded_file:
    # Load data
    data = load_data(uploaded_file)
    
    if data is not None:
        # Process data into a tree structure based on the category columns
        category_tree = process_data(data)

        # Create markmap content
        markmap_content = """
        ---
        markmap:
          colorFreezeLevel: 2
          color: '#1f77b4'
          initialExpandLevel: 3
        ---
        # URL Hierarchy
        """ + create_markmap_content(category_tree)

        # Streamlit UI
        st.title("Hierarchical Visualization of URLs with Counts and Colors")

        # CSS to control the size of the markmap and hide URLs
        st.markdown("""
            <style>
            .stMarkmap > div {
                height: 600px;
                width: 100%;
            }
            .markmap-node-text:not(:hover) .mm-url {
                display: none;
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
        st.error("Failed to load data. Please check your file format and content.")
else:
    st.info("Please upload an Excel file to start.")

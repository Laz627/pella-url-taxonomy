import streamlit as st
import pandas as pd
from streamlit_markmap import markmap
import io

# Set page config at the very beginning
st.set_page_config(layout="wide", page_title="URL Taxonomy Visualizer")

def create_template():
    df = pd.DataFrame({
        'Full URL': ['https://example.com/page1', 'https://example.com/page2'],
        'L1': ['Category1', 'Category1'],
        'L2': ['Subcategory1', 'Subcategory2'],
        'L3': ['SubSubcategory1', 'SubSubcategory2'],
        'L4': ['', ''],
        'L5': ['', ''],
        'L6': ['', ''],
        'L7': ['', ''],
        'L8': ['', '']
    })
    return df

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            data = data.drop_duplicates(subset=['Full URL'])
            st.success(f"Data loaded successfully. Shape after removing duplicates: {data.shape}")
            return data
        except Exception as e:
            st.error(f"An error occurred while loading the data: {str(e)}")
            return None
    else:
        st.warning("No file uploaded. Please upload an Excel file.")
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
            if level < 3:
                if '_urls' in value and value['_urls']:
                    content += f"{'  ' * (level + 1)}- URLs\n"
                    for url in sorted(value['_urls']):
                        content += f"{'  ' * (level + 2)}- {url}\n"
                content += create_markmap_content(value, level + 1)
    return content

def process_data(data):
    required_columns = ['Full URL'] + [f'L{i}' for i in range(1, 9)]
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        st.error(f"The following required columns are missing from the uploaded file: {', '.join(missing_columns)}")
        st.error("Please ensure your Excel file has the correct column names and try again.")
        return None

    category_tree = {}
    problematic_urls = []
    for _, row in data.iterrows():
        url = row['Full URL']
        category_path = [str(row[f'L{i}']) for i in range(1, 9) if f'L{i}' in row.index and pd.notna(row[f'L{i}']) and row[f'L{i}'] != '']
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

# Download template
st.subheader("Download Template")
template_df = create_template()
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    template_df.to_excel(writer, index=False, sheet_name='Sheet1')
buffer.seek(0)
st.download_button(
    label="Download Excel Template",
    data=buffer,
    file_name="url_taxonomy_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# File uploader
st.subheader("Upload Your Excel File")
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    if data is not None:
        st.write("Sample of the loaded data:")
        st.write(data.head())

        st.write("Column names:")
        st.write(data.columns.tolist())

        # Process data into a tree structure based on the category columns
        category_tree = process_data(data)

        if category_tree is not None:
            st.write("Category tree structure:")
            st.write(category_tree)

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

            st.write("Markmap content:")
            st.text(markmap_content)

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
    st.info("Please upload an Excel file to visualize the URL taxonomy.")

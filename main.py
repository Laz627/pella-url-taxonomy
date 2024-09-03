import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path to match your GitHub repository structure
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'  # Ensure this path matches where your file is stored
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Graphviz
def build_hierarchy_graph(data):
    dot = Digraph()
    dot.attr(compound='true', rankdir='LR')  # Left to Right orientation

    # Track added nodes to avoid duplication
    added_nodes = set()

    # Iterate through each row to build the hierarchy
    for index, row in data.iterrows():
        # Root node: Page Topic
        root = row['Page Topic']
        if root not in added_nodes:
            dot.node(root, root)  # Add root node
            added_nodes.add(root)

        # Add hierarchical levels
        parent = root  # Start with the root node as the parent
        for level in range(1, 8):
            level_col = f'L{level}'
            child = row.get(level_col)
            if pd.notna(child):
                if child not in added_nodes:
                    dot.node(child, child)  # Add child node
                    added_nodes.add(child)
                dot.edge(parent, child)  # Create edge between parent and child
                parent = child  # Update parent for the next level

    return dot

# Load data
data = load_data()

# Build hierarchical data graph
hierarchy_graph = build_hierarchy_graph(data)

# Streamlit UI
st.title('Hierarchical Visualization of URLs using Collapsible Tree Diagram')

st.markdown("""
The collapsible tree diagram below allows you to explore the hierarchy. Click on the nodes to collapse or expand them.
""")

# Render the Graphviz tree
st.graphviz_chart(hierarchy_graph)

# Provide user interaction for opening URLs
st.markdown("""
### Click on the URLs below to navigate
""")

selected_url = st.selectbox('Select URL to open', data['Full URL'].unique())
if st.button('Open URL'):
    st.write(f"Opening URL: {selected_url}")
    st.write(f"<script>window.open('{selected_url}');</script>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path to match your GitHub repository structure
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'  # Ensure this path matches where your file is stored
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Pyvis Network
def build_hierarchy_network(data, max_depth=3):
    # Initialize the Pyvis Network with performance settings
    net = Network(height='800px', width='100%', directed=True, notebook=False)
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=100, spring_strength=0.1)
    
    # Track added nodes to avoid duplication
    added_nodes = set()

    # Iterate through each row to build the hierarchy
    for index, row in data.iterrows():
        # Root node: Page Topic
        root = row['Page Topic']
        if root not in added_nodes:
            net.add_node(root, label=root, title=row['Full URL'])
            added_nodes.add(root)

        # Add hierarchical levels up to the specified max_depth
        parent = root  # Start with the root node as the parent
        for level in range(1, max_depth + 1):
            level_col = f'L{level}'
            child = row.get(level_col)
            if pd.notna(child) and child != '':
                unique_child = f"{child}_{index}"  # Ensure unique ID for nodes
                if unique_child not in added_nodes:
                    net.add_node(unique_child, label=child, title=row['Full URL'])
                    added_nodes.add(unique_child)
                net.add_edge(parent, unique_child)  # Create edge between parent and child
                parent = unique_child  # Update parent for the next level

    # Customize network options for better visualization
    net.set_options("""
    var options = {
      "nodes": {
        "color": {
          "border": "rgba(0,0,0,1)",
          "background": "rgba(220,220,220,1)"
        },
        "font": {
          "size": 12
        }
      },
      "edges": {
        "color": {
          "color": "rgba(150,150,150,1)"
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)
    
    return net

# Load data
data = load_data()

# Streamlit UI
st.title('Hierarchical Visualization of URLs using Collapsible Tree Diagram')

st.markdown("""
The collapsible tree diagram below allows you to explore the hierarchy. Use the controls to adjust the depth of the tree to display.
""")

# User input to control the depth of the hierarchy displayed
max_depth = st.slider('Select depth of the hierarchy to display', min_value=1, max_value=7, value=3)

# Build hierarchical data network with user-specified depth
hierarchy_network = build_hierarchy_network(data, max_depth=max_depth)

# Save and display the Pyvis network in Streamlit
hierarchy_network.save_graph('network.html')

# Display the network using Streamlit's components
components.html(open('network.html', 'r').read(), height=800)

# Provide user interaction for opening URLs
st.markdown("""
### Click on the URLs below to navigate
""")

selected_url = st.selectbox('Select URL to open', data['Full URL'].unique())
if st.button('Open URL'):
    st.write(f"Opening URL: {selected_url}")
    st.write(f"<script>window.open('{selected_url}');</script>", unsafe_allow_html=True)

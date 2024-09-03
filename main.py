import streamlit as st
import pandas as pd
from bokeh.plotting import figure, from_networkx
from bokeh.models import Plot, Range1d, Circle, MultiLine, HoverTool
from bokeh.palettes import Spectral8
from bokeh.io import show
import networkx as nx

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path to match your GitHub repository structure
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'  # Ensure this path matches where your file is stored
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Bokeh and NetworkX
def build_hierarchy_graph(data):
    # Create a directed graph
    G = nx.DiGraph()
    
    # Track added nodes to avoid duplication
    added_nodes = set()

    # Iterate through each row to build the hierarchy
    for index, row in data.iterrows():
        # Root node: Page Topic
        root = row['Page Topic']
        if root not in added_nodes:
            G.add_node(root, title=row['Full URL'])  # Add root node
            added_nodes.add(root)

        # Add hierarchical levels
        parent = root  # Start with the root node as the parent
        for level in range(1, 8):
            level_col = f'L{level}'
            child = row.get(level_col)
            if pd.notna(child) and child != '':
                unique_child = f"{child}_{index}"  # Ensure unique ID for nodes
                if unique_child not in added_nodes:
                    G.add_node(unique_child, title=row['Full URL'])  # Add child node
                    added_nodes.add(unique_child)
                G.add_edge(parent, unique_child)  # Create edge between parent and child
                parent = unique_child  # Update parent for the next level

    return G

# Load data
data = load_data()

# Build hierarchical data graph
G = build_hierarchy_graph(data)

# Plotting with Bokeh
plot = Plot(width=800, height=800, x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
plot.title.text = "Hierarchical URL Visualization"

# Add node renderer
graph_renderer = from_networkx(G, nx.spring_layout, scale=2, center=(0,0))
plot.renderers.append(graph_renderer)

# Add HoverTool to display URL on hover
hover = HoverTool(tooltips=[("URL", "@title")])
plot.add_tools(hover)

# Streamlit UI
st.title('Hierarchical Visualization of URLs using Bokeh')

st.bokeh_chart(plot)

# Provide user interaction for opening URLs
st.markdown("""
### Click on the URLs below to navigate
""")

selected_url = st.selectbox('Select URL to open', data['Full URL'].unique())
if st.button('Open URL'):
    st.write(f"Opening URL: {selected_url}")
    st.write(f"<script>window.open('{selected_url}');</script>", unsafe_allow_html=True)

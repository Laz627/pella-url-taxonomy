import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path to match your GitHub repository structure
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'  # Ensure this path matches where your file is stored
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Plotly Tree Diagram
def build_hierarchy(data):
    hierarchy = {
        "Full URL": [],
        "Page Topic": [],
        "L1": [],
        "L2": [],
        "L3": [],
        "L4": [],
        "L5": [],
        "L6": [],
        "L7": []
    }
    
    # Iterate through each row to build the hierarchy
    for index, row in data.iterrows():
        # Extract the Full URL, Page Topic, and hierarchical levels (L1, L2, L3, etc.)
        hierarchy['Full URL'].append(row['Full URL'])
        hierarchy['Page Topic'].append(row['Page Topic'])
        
        # Add levels (L1 to L7), filling only until the first non-empty level is encountered
        for level in range(1, 8):
            level_col = f'L{level}'
            # Check if this level exists in the data and is not NaN
            if level_col in row and pd.notna(row[level_col]):
                hierarchy[level_col].append(row[level_col])
            else:
                # Fill remaining levels with None if there are no more children
                hierarchy[level_col].append(None)
    
    # Convert to DataFrame
    hierarchy_df = pd.DataFrame(hierarchy)

    # Remove non-leaf nodes with missing children (invalid hierarchical paths)
    for level in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        # If a node at this level has children but is missing any of them, it is considered invalid
        hierarchy_df = hierarchy_df[~((hierarchy_df[level].notna()) & (hierarchy_df[level].shift(-1).isna()))]

    return hierarchy_df

# Function to generate the Plotly Tree Diagram
def create_tree_diagram(hierarchy_df):
    # Define the nodes and edges for the tree diagram
    nodes = []
    edges = []
    
    # Create nodes for each unique value in each level
    def add_node(parent, child, url):
        if child not in nodes:
            nodes.append(child)
            edges.append((parent, child, url))

    # Root node
    for i, row in hierarchy_df.iterrows():
        root = row['Page Topic']
        add_node('', root, row['Full URL'])  # Root has no parent
        
        # Add child nodes
        for level in range(1, 8):
            parent = row[f'L{level-1}'] if level > 1 else root
            child = row[f'L{level}']
            if pd.notna(child):
                add_node(parent, child, row['Full URL'])

    # Generate the figure using Plotly
    fig = go.Figure()

    # Add trace for each node with hover functionality
    for parent, child, url in edges:
        fig.add_trace(go.Scatter(
            x=[parent, child],
            y=[0, 1],
            text=f'<a href="{url}">{child}</a>',
            mode='markers+lines',
            hoverinfo='text'
        ))

    # Set layout for collapsible tree diagram
    fig.update_layout(
        title="Collapsible Tree Diagram of URLs",
        showlegend=False,
        xaxis=dict(showline=False, zeroline=False),
        yaxis=dict(showline=False, zeroline=False)
    )

    return fig

# Load data
data = load_data()

# Build hierarchical data
hierarchy_df = build_hierarchy(data)

# Streamlit UI
st.title('Hierarchical Visualization of URLs using Collapsible Tree Diagram')

st.markdown("""
Click on a node in the Tree diagram to drill down and explore the hierarchy.
""")

# Create and display the Tree diagram
fig = create_tree_diagram(hierarchy_df)

# Display the plot
st.plotly_chart(fig)

# Provide user interaction for opening URLs
st.markdown("""
### Click on the URLs below to navigate
""")

selected_url = st.selectbox('Select URL to open', hierarchy_df['Full URL'].unique())
if st.button('Open URL'):
    st.write(f"Opening URL: {selected_url}")
    st.write(f"<script>window.open('{selected_url}');</script>", unsafe_allow_html=True)

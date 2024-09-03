import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path if needed
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Plotly Treemap
def build_hierarchy(data):
    hierarchy = {
        "labels": [],
        "parents": [],
        "ids": [],
        "urls": []
    }
    
    # Iterate through each row to build the hierarchy
    for index, row in data.iterrows():
        # Extract the Full URL, Page Topic, and hierarchical levels (L0, L1, L2, etc.)
        full_url = row['Full URL']
        page_topic = row['Page Topic']
        
        # Add the root node
        hierarchy['labels'].append(page_topic)
        hierarchy['parents'].append('')
        hierarchy['ids'].append(page_topic)
        hierarchy['urls'].append(full_url)
        
        # Add child nodes (L1, L2, L3, etc.)
        for level in range(1, len(row) - 2):  # Exclude 'Full URL' and 'Page Topic'
            if not pd.isna(row[f'L{level}']):
                current_label = row[f'L{level}']
                parent_label = row[f'L{level - 1}'] if level > 1 else page_topic
                
                # Only add if not already in labels
                if current_label not in hierarchy['labels']:
                    hierarchy['labels'].append(current_label)
                    hierarchy['parents'].append(parent_label)
                    hierarchy['ids'].append(current_label)
                    hierarchy['urls'].append(full_url)
    
    return hierarchy

# Function to generate the Plotly Treemap
def create_treemap(hierarchy):
    fig = go.Figure(go.Treemap(
        labels=hierarchy['labels'],
        parents=hierarchy['parents'],
        ids=hierarchy['ids'],
        hovertext=hierarchy['urls'],
        customdata=hierarchy['urls'],
        hoverinfo='label+text',
        marker=dict(colorscale='Viridis'),
    ))

    fig.update_traces(root_color="lightgrey")
    
    return fig

# Load data
data = load_data()

# Build hierarchical data
hierarchy = build_hierarchy(data)

# Streamlit UI
st.title('Hierarchical Visualization of URLs')

st.markdown("""
Click on a node in the treemap to navigate to the corresponding URL.
""")

# Create and display the treemap
fig = create_treemap(hierarchy)

def on_click(trace, points, state):
    url = points.customdata[points.point_inds[0]]
    st.write(f"Opening URL: {url}")
    st.write(f"<script>window.open('{url}')</script>", unsafe_allow_html=True)

fig.data[0].on_click(on_click)

# Display the plot
st.plotly_chart(fig)

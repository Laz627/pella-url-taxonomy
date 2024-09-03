import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data from the Excel file
@st.cache_data
def load_data():
    # Update the file path to match your GitHub repository structure
    file_path = 'URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm'  # Ensure this path matches where your file is stored
    data = pd.read_excel(file_path)
    return data

# Create a function to build hierarchical data for Plotly Sunburst
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
        
        # Add levels (L1 to L7), ensuring any level is filled with 'None' if it is missing children
        for level in range(1, 8):
            level_col = f'L{level}'
            if pd.notna(row.get(level_col)):
                hierarchy[level_col].append(row[level_col])
            else:
                # Fill remaining levels with None if there are no more children to avoid "non-leaves" errors
                hierarchy[level_col].append(None)
    
    return pd.DataFrame(hierarchy)

# Function to generate the Plotly Sunburst Chart
def create_sunburst(hierarchy_df):
    # Filter out rows where intermediate levels are empty to avoid errors
    for level in ['L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1']:
        # Set to None if it is a non-leaf node with no children
        hierarchy_df.loc[hierarchy_df[level].isna(), level] = None
        
    # Create Sunburst chart
    fig = px.sunburst(
        hierarchy_df,
        path=['Page Topic', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'],
        hover_name='Full URL',
        color='Page Topic',
        branchvalues='total',
        title='Hierarchical Visualization of URLs - Sunburst'
    )
    return fig

# Load data
data = load_data()

# Build hierarchical data
hierarchy_df = build_hierarchy(data)

# Streamlit UI
st.title('Hierarchical Visualization of URLs using Sunburst Chart')

st.markdown("""
Click on a node in the Sunburst chart to drill down and explore the hierarchy.
""")

# Create and display the Sunburst chart
fig = create_sunburst(hierarchy_df)

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

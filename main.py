import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import requests
from io import BytesIO

@st.cache_data
def load_data():
    # GitHub raw content URL for your Excel file
    url = "URL_Subfolder_Breakdown_With_Full_URL_and_Topic.xlsm"
    
    response = requests.get(url)
    content = BytesIO(response.content)
    
    # Read the Excel file
    data = pd.read_excel(content, engine='openpyxl')
    return data

def create_tree_structure(data):
    nodes = []
    edges = []
    
    # Create a root node
    root_node = Node(id="root", label="Website Root", size=20)
    nodes.append(root_node)
    
    for _, row in data.iterrows():
        parent = "root"
        for level in ['Page Topic', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']:
            if pd.notna(row[level]) and row[level] != '':
                node_id = f"{parent}_{row[level]}"
                if not any(node.id == node_id for node in nodes):
                    nodes.append(Node(id=node_id, label=str(row[level]), size=15))
                    edges.append(Edge(source=parent, target=node_id))
                parent = node_id
            else:
                break
    
    return nodes, edges

# Main app
st.title('Website Taxonomy Visualization')

try:
    data = load_data()
    st.write("Data loaded successfully. Shape:", data.shape)
    st.write("Columns:", data.columns.tolist())

    nodes, edges = create_tree_structure(data)

    config = Config(width=800,
                    height=600,
                    directed=True,
                    physics=True,
                    hierarchical=True,
                    nodeHighlightBehavior=True, 
                    highlightColor="#F7A7A6",
                    collapsible=True)

    agraph(nodes=nodes, 
           edges=edges, 
           config=config)

    # Add a search functionality
    search_term = st.text_input("Search for a page or section:")
    if search_term:
        filtered_nodes = [node for node in nodes if search_term.lower() in node.label.lower()]
        if filtered_nodes:
            st.write("Matching nodes:")
            for node in filtered_nodes:
                st.write(node.label)
        else:
            st.write("No matching nodes found.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.error("Please check if the GitHub URL is correct and the file is accessible.")

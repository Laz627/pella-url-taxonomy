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

# Main logic
if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    if data is not None:
        # Process data into a tree structure based on the category columns
        category_tree = process_data(data)

        if category_tree is not None:
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

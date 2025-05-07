import streamlit as st
import requests
import os
from datetime import datetime
import json

# API Configuration
API_BASE_URL = "http://localhost:8000/api"  # Updated to match FastAPI router prefix

def main():
    st.set_page_config(
        page_title="Malagasy Customs Document Management",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 Malagasy Customs Document Management System")
    st.markdown("---")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Document", "View Documents", "Search Documents"])

    if page == "Upload Document":
        upload_document()
    elif page == "View Documents":
        view_documents()
    else:
        search_documents()

def upload_document():
    st.header("Upload New Document")
    
    with st.form("upload_form"):
        bsc_number = st.text_input("BSC Number")
        category = st.selectbox(
            "Document Category",
            ["INV","PCK","BIL","DED","DOM","DAU","OTH"]
        )
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "jpg", "jpeg"])
        
        submitted = st.form_submit_button("Upload")
        
        if submitted and uploaded_file is not None:
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                
                # Send bsc_number and category as query parameters
                response = requests.post(
                    f"{API_BASE_URL}/documents/upload?bsc_number={bsc_number}&category={category}",
                    files=files
                )
                
                if response.status_code == 200:
                    st.success("Document uploaded successfully!")
                else:
                    st.error(f"Error uploading document: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def view_documents():
    st.header("View All Documents")
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents/list")
        
        if response.status_code == 200:
            documents = response.json()
            
            if not documents:
                st.info("No documents found.")
                return
                
            # Example: function to handle document download
            def download_document(doc_uuid):
                st.success(f"✅ Download for document {doc_uuid} started!")

            # Loop through documents and display details
            for doc in documents:
                bsc_number = doc.get('bsc_number', 'N/A')
                category = doc.get('category', 'N/A')
                upload_date = doc.get('upload_datetime', 'N/A')
                filesize = doc.get('filesize', 'N/A')
                page_number = doc.get('page_number', 'N/A')
                doc_uuid = doc.get('uuid')

                # Clean expander title
                with st.expander(f"📄 Document | 🔖 BSC: {bsc_number} | 📂 Type: {category}"):
                    col1, col2 = st.columns(2)

                    # Left column — document metadata
                    with col1:
                        st.markdown("### 📑 Document Info")
                        st.markdown(f"**🔖 BSC Number:** `{bsc_number}`")
                        st.markdown(f"**📂 Category:** `{category}`")
                        st.markdown(f"**🗓️ Upload Date:** `{upload_date}`")

                    # Right column — technical metadata
                    with col2:
                        st.markdown("### ⚙️ File Details")
                        st.markdown(f"**📦 File Size:** `{filesize}`")
                        st.markdown(f"**📄 Pages:** `{page_number}`")

                    # Horizontal separator
                    st.markdown("---")

                    # Download button
                    download_document(doc_uuid)
        else:
            st.error(f"Error fetching documents: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def search_documents():
    st.header("Search Documents")
    
    with st.form("search_form"):
        bsc_number = st.text_input("BSC Number")
        category = st.selectbox(
            "Category",
            ["All", "INV", "PCK", "BIL", "DED", "DOM", "DAU", "OTH"]
        )
        
        submitted = st.form_submit_button("Search")
        
        if submitted:
            try:
                params = {}
                if bsc_number:
                    params["bsc_number"] = bsc_number
                if category != "All":
                    params["category"] = category
                
                response = requests.get(
                    f"{API_BASE_URL}/documents/search",
                    params=params
                )
                
                if response.status_code == 200:
                    documents = response.json()
                    
                    if not documents:
                        st.info("No documents found matching your criteria.")
                        return
                        
                    for doc in documents:
                        with st.expander(f"Document: {doc.get('filename', 'N/A')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**BSC Number:** {doc.get('bsc_number', 'N/A')}")
                                st.write(f"**Category:** {doc.get('category', 'N/A')}")
                                st.write(f"**Upload Date:** {doc.get('upload_datetime', 'N/A')}")
                            with col2:
                                st.write(f"**File Size:** {doc.get('filesize', 'N/A')}")
                                st.write(f"**Pages:** {doc.get('page_number', 'N/A')}")
                                
                            if st.button("Download", key=f"search_download_{doc.get('uuid')}"):
                                download_document(doc.get('uuid'))
                else:
                    st.error(f"Error searching documents: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def download_document(doc_uuid):
    try:
        response = requests.get(f"{API_BASE_URL}/documents/download/{doc_uuid}")
        
        if response.status_code == 200:
            # Get filename from headers or use a default
            filename = response.headers.get('content-disposition', '').split('filename=')[-1]
            if not filename:
                filename = f"document_{doc_uuid}.pdf"
            
            # Create a download button with the file content
            st.download_button(
                label="📥 Download File",
                data=response.content,
                file_name=filename,
                mime=response.headers.get('content-type', 'application/octet-stream'),
                key=f"download_btn_{doc_uuid}"
            )
        else:
            st.error(f"Error downloading document: {response.text}")
    except Exception as e:
        st.error(f"An error occurred while downloading: {str(e)}")

if __name__ == "__main__":
    main() 
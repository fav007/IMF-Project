import streamlit as st
import requests
import os
from datetime import datetime
import json

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"  # Update this with your actual API URL

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
                data = {
                    "bsc_number": bsc_number,
                    "category": category
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/documents/upload",
                    files=files,
                    data=data
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
                
            for doc in documents:
                with st.expander(f"Document: {doc.get('filename', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**BSC Number:** {doc.get('bsc_number', 'N/A')}")
                        st.write(f"**Category:** {doc.get('category', 'N/A')}")
                        st.write(f"**Upload Date:** {doc.get('upload_date', 'N/A')}")
                    with col2:
                        st.write(f"**File Size:** {doc.get('file_size', 'N/A')} MB")
                        st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                        
                    if st.button("Download", key=f"download_{doc.get('id')}"):
                        download_document(doc.get('id'))
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
            ["All", "Import", "Export", "Transit", "Other"]
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
                                st.write(f"**Upload Date:** {doc.get('upload_date', 'N/A')}")
                            with col2:
                                st.write(f"**File Size:** {doc.get('file_size', 'N/A')} MB")
                                st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                                
                            if st.button("Download", key=f"search_download_{doc.get('id')}"):
                                download_document(doc.get('id'))
                else:
                    st.error(f"Error searching documents: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def download_document(doc_id):
    try:
        response = requests.get(f"{API_BASE_URL}/documents/download/{doc_id}")
        
        if response.status_code == 200:
            # Get filename from headers
            filename = response.headers.get('content-disposition', '').split('filename=')[-1]
            if not filename:
                filename = f"document_{doc_id}.pdf"
                
            # Create downloads directory if it doesn't exist
            os.makedirs("downloads", exist_ok=True)
            
            # Save the file
            file_path = os.path.join("downloads", filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
                
            st.success(f"Document downloaded successfully to {file_path}")
        else:
            st.error(f"Error downloading document: {response.text}")
    except Exception as e:
        st.error(f"An error occurred while downloading: {str(e)}")

if __name__ == "__main__":
    main() 
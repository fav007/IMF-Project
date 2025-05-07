import streamlit as st
import requests
import os
from datetime import datetime

# ============================
# 📦 API Configuration
# ============================
API_BASE_URL = "http://localhost:8000/api"

# ============================
# 📄 Streamlit App Entry Point
# ============================
def main():
    st.set_page_config(
        page_title="📄 Malagasy Customs Document Management",
        page_icon="📂",
        layout="wide"
    )

    st.title("📂 Malagasy Customs Document Management System")
    st.markdown("---")

    # Sidebar Navigation
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["📤 Upload Document", "📑 View Documents", "🔍 Search Documents"])

    if page == "📤 Upload Document":
        upload_document()
    elif page == "📑 View Documents":
        view_documents()
    elif page == "🔍 Search Documents":
        search_documents()

# ============================
# 📤 Document Upload Page
# ============================
def upload_document():
    st.header("📤 Upload New Document")

    with st.form("upload_form"):
        bsc_number = st.text_input("BSC Number")
        category = st.selectbox(
            "Document Category",
            ["INV", "PCK", "BIL", "DED", "DOM", "DAU", "OTH"]
        )
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "jpg", "jpeg"])

        submitted = st.form_submit_button("📤 Upload Document")

        if submitted:
            if not uploaded_file:
                st.warning("📌 Please select a file to upload.")
                return

            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(
                    f"{API_BASE_URL}/documents/upload?bsc_number={bsc_number}&category={category}",
                    files=files
                )

                if response.status_code == 200:
                    st.success("✅ Document uploaded successfully!")
                else:
                    st.error(f"❌ Error uploading document: {response.text}")
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")

# ============================
# 📑 View Documents Page
# ============================
def view_documents():
    st.header("📑 View All Documents")

    try:
        response = requests.get(f"{API_BASE_URL}/documents/list")

        if response.status_code == 200:
            documents = response.json()

            if not documents:
                st.info("📂 No documents found.")
                return

            st.success(f"📊 {len(documents)} documents found.")
            for doc in documents:
                display_document_card(doc)
        else:
            st.error(f"❌ Error fetching documents: {response.text}")
    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")

# ============================
# 🔍 Search Documents Page
# ============================
def search_documents():
    st.header("🔍 Search Documents")

    with st.form("search_form"):
        bsc_number = st.text_input("BSC Number")
        category = st.selectbox(
            "Document Category",
            ["All", "INV", "PCK", "BIL", "DED", "DOM", "DAU", "OTH"]
        )

        submitted = st.form_submit_button("🔍 Search")

        if submitted:
            try:
                params = {}
                if bsc_number:
                    params["bsc_number"] = bsc_number
                if category != "All":
                    params["category"] = category

                response = requests.get(f"{API_BASE_URL}/documents/search", params=params)

                if response.status_code == 200:
                    documents = response.json()

                    if not documents:
                        st.info("📂 No documents match your search criteria.")
                        return

                    st.success(f"🔍 {len(documents)} documents found.")
                    for doc in documents:
                        display_document_card(doc)
                else:
                    st.error(f"❌ Error during search: {response.text}")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")

# ============================
# 📑 Document Card Display Helper
# ============================
def display_document_card(doc):
    """Display a document's metadata and actions inside an expander."""
    bsc_number  = doc.get('bsc_number', 'N/A')
    category    = doc.get('category', 'N/A')
    upload_date = doc.get('upload_datetime', 'N/A')
    filesize    = doc.get('filesize', 'N/A')
    page_number = doc.get('page_number', 'N/A')
    doc_uuid    = doc.get('uuid')
    filename    = doc.get('filename', f"Document_{doc_uuid}")

    with st.expander(f"📄 Document | 🔖 BSC: {bsc_number} | 📂 Type: {category}"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📑 Document Info")
            st.markdown(f"**🔖 BSC Number:** `{bsc_number}`")
            st.markdown(f"**📂 Category:** `{category}`")
            st.markdown(f"**🗓️ Upload Date:** `{upload_date}`")

        with col2:
            st.markdown("### ⚙️ File Details")
            st.markdown(f"**📦 File Size:** `{filesize}`")
            st.markdown(f"**📄 Pages:** `{page_number}`")

        st.markdown("---")

        if st.button("📥 Download Document", key=f"download_{doc_uuid}"):
            download_document(doc_uuid)

# ============================
# 📥 Document Download Handler
# ============================
def download_document(doc_uuid):
    """Download a document by its UUID."""
    try:
        print(doc_uuid)
        response = requests.get(f"{API_BASE_URL}/documents/download/{doc_uuid}")

        if response.status_code == 200:
            filename = response.headers.get('content-disposition', '').split('filename=')[-1]
            if not filename:
                filename = f"document_{doc_uuid}.pdf"

            os.makedirs("downloads", exist_ok=True)
            file_path = os.path.join("downloads", filename)

            with open(file_path, "wb") as f:
                f.write(response.content)

            st.success(f"✅ Document downloaded successfully to `{file_path}`")
        else:
            st.error(f"❌ Error downloading document: {response.text}")
    except Exception as e:
        st.error(f"⚠️ An error occurred while downloading: {str(e)}")

# ============================
# 🚀 Run Streamlit App
# ============================
if __name__ == "__main__":
    main()

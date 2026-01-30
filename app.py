import streamlit as st
import json
from datetime import datetime
from langchain_openai import AzureChatOpenAI
import os
from config import Config

# Page Configuration
st.set_page_config(
    page_title="Dynamic API Documentation Generator",
    page_icon="📚",
    layout="wide"
)

# Title and Description
st.title("📚 Dynamic API Documentation Generator")
st.markdown("### AI-Powered API Documentation using Azure OpenAI")
st.markdown("Generate professional API documentation instantly!")

# Sidebar for Azure OpenAI Configuration
st.sidebar.header("⚙️ Azure OpenAI Configuration")
# PRE-FILL WITH VALUES FROM CONFIG.PY
azure_endpoint = st.sidebar.text_input(
    "Azure OpenAI Endpoint",
    value=Config.AZURE_ENDPOINT,
    help="Your Azure OpenAI endpoint URL"
)

azure_api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    value=Config.AZURE_API_KEY,
    help="Your Azure OpenAI API key"
)

azure_deployment = st.sidebar.text_input(
    "Deployment Name",
    value=Config.AZURE_DEPLOYMENT,
    help="Your deployment name (e.g., gpt-4, gpt-35-turbo)"
)

api_version = st.sidebar.text_input(
    "API Version",
    value=Config.AZURE_API_VERSION,
    help="Azure OpenAI API version"
)
# Initialize session state
if 'docs_storage' not in st.session_state:
    st.session_state.docs_storage = []

if 'generated_doc' not in st.session_state:
    st.session_state.generated_doc = None


# API Documentation Generator Class
class APIDocGenerator:
    def __init__(self, endpoint, api_key, deployment, api_version):
        """Initialize the API Documentation Generator"""
        self.client = AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment_name=deployment,
            temperature=1
        )
        self.deployment = deployment
    
    def generate_documentation(self, api_name, method, endpoint, description="", parameters=None):
        """Generate documentation for an API endpoint using Azure OpenAI"""
        
        prompt = f"""Generate professional API documentation for the following endpoint:

API Name: {api_name}
HTTP Method: {method}
Endpoint: {endpoint}
Description: {description}
Parameters: {parameters if parameters else 'None'}

Please provide:
1. A clear description of what this API does
2. Request format and examples
3. Response format and examples
4. Possible error codes
5. Usage notes

Format the output in a clear, professional manner."""

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="You are an expert API documentation writer. Create clear, concise, and professional API documentation."),
                HumanMessage(content=prompt)
            ]
            
            response = self.client.invoke(messages)
            documentation = response.content
            
            doc_entry = {
                "api_name": api_name,
                "method": method,
                "endpoint": endpoint,
                "description": description,
                "parameters": parameters,
                "generated_doc": documentation,
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.docs_storage.append(doc_entry)
            
            return documentation
            
        except Exception as e:
            return f"Error generating documentation: {str(e)}"


# Main App Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Generate Docs", "📄 View All Docs", "💾 Save/Load", "📖 Example"])

# Tab 1: Generate Documentation
with tab1:
    st.header("Generate API Documentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_name = st.text_input("API Name", placeholder="e.g., User Login")
        method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
        endpoint = st.text_input("Endpoint", placeholder="e.g., /api/v1/users")
    
    with col2:
        description = st.text_area("Description", placeholder="What does this API do?")
        parameters_input = st.text_area(
            "Parameters (JSON format)",
            placeholder='{"param1": "type", "param2": "type"}',
            help="Enter parameters in JSON format"
        )
    
    if st.button("🚀 Generate Documentation", type="primary"):
        if not azure_api_key or azure_api_key == "":
            st.error("❌ Please enter your Azure OpenAI API Key in the sidebar!")
        elif not api_name or not endpoint:
            st.error("❌ Please fill in API Name and Endpoint!")
        else:
            with st.spinner("Generating documentation using AI..."):
                try:
                    # Parse parameters
                    parameters = None
                    if parameters_input.strip():
                        try:
                            parameters = json.loads(parameters_input)
                        except:
                            st.warning("⚠️ Invalid JSON for parameters, using as text")
                            parameters = parameters_input
                    
                    # Generate documentation
                    doc_gen = APIDocGenerator(azure_endpoint, azure_api_key, azure_deployment, api_version)
                    documentation = doc_gen.generate_documentation(
                        api_name, method, endpoint, description, parameters
                    )
                    
                    st.session_state.generated_doc = documentation
                    st.success("✅ Documentation generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display generated documentation
    if st.session_state.generated_doc:
        st.markdown("---")
        st.subheader("📄 Generated Documentation")
        st.markdown(st.session_state.generated_doc)

# Tab 2: View All Documentation
with tab2:
    st.header("All Generated Documentation")
    
    if not st.session_state.docs_storage:
        st.info("ℹ️ No documentation generated yet. Go to 'Generate Docs' tab to create your first documentation!")
    else:
        st.success(f"📚 Total Documents: {len(st.session_state.docs_storage)}")
        
        for i, doc in enumerate(st.session_state.docs_storage, 1):
            with st.expander(f"📄 {i}. {doc['api_name']} - {doc['method']} {doc['endpoint']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**API Name:** {doc['api_name']}")
                    st.markdown(f"**Method:** {doc['method']}")
                    st.markdown(f"**Endpoint:** {doc['endpoint']}")
                
                with col2:
                    st.markdown(f"**Description:** {doc['description']}")
                    st.markdown(f"**Generated:** {doc['timestamp']}")
                
                st.markdown("---")
                st.markdown("**Generated Documentation:**")
                st.markdown(doc['generated_doc'])

# Tab 3: Save/Load
with tab3:
    st.header("Save & Load Documentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💾 Save Documentation")
        filename = st.text_input("Filename", value="api_documentation.json")
        
        if st.button("Save to File"):
            if st.session_state.docs_storage:
                try:
                    with open(filename, 'w') as f:
                        json.dump(st.session_state.docs_storage, f, indent=2)
                    st.success(f"✅ Documentation saved to {filename}")
                except Exception as e:
                    st.error(f"❌ Error saving file: {str(e)}")
            else:
                st.warning("⚠️ No documentation to save!")
    
    with col2:
        st.subheader("📂 Load Documentation")
        load_filename = st.text_input("Load from file", value="api_documentation.json", key="load_file")
        
        if st.button("Load from File"):
            try:
                with open(load_filename, 'r') as f:
                    st.session_state.docs_storage = json.load(f)
                st.success(f"✅ Loaded {len(st.session_state.docs_storage)} documents from {load_filename}")
            except FileNotFoundError:
                st.error(f"❌ File {load_filename} not found!")
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
    
    # Download button
    if st.session_state.docs_storage:
        st.markdown("---")
        json_str = json.dumps(st.session_state.docs_storage, indent=2)
        st.download_button(
            label="⬇️ Download Documentation (JSON)",
            data=json_str,
            file_name="api_documentation.json",
            mime="application/json"
        )

# Tab 4: Example
with tab4:
    st.header("📖 Example: Sum Calculator API")
    
    st.markdown("""
    ### How It Works
    
    **Step-by-Step Flow:**
    
    1. **You Provide Input** → API details (name, method, endpoint, parameters)
    2. **System Creates Prompt** → Formats your input for Azure OpenAI
    3. **Azure OpenAI Processes** → AI generates professional documentation
    4. **Documentation Returned** → Complete API docs with examples
    5. **Stored Locally** → Saved in memory and optionally to JSON file
    
    ---
    
    ### Example Input
    
    **API Name:** Sum Calculator  
    **Method:** POST  
    **Endpoint:** /api/v1/calculator/sum  
    **Description:** Calculates the sum of two numbers  
    **Parameters:**
    ```json
    {
        "number1": "integer - First number to add",
        "number2": "integer - Second number to add"
    }
    ```
    
    ---
    
    ### Example Output (AI-Generated)
    
    The AI will generate comprehensive documentation like:
    
    **API Documentation: Sum Calculator**
    
    **Description:**  
    This endpoint accepts two numeric values and returns their sum.
    
    **Request Format:**
    ```json
    POST /api/v1/calculator/sum
    Content-Type: application/json
    
    {
      "number1": 5,
      "number2": 10
    }
    ```
    
    **Response Format:**
    ```json
    {
      "result": 15,
      "status": "success"
    }
    ```
    
    **Possible Error Codes:**
    - 400: Bad Request (invalid parameters)
    - 422: Unprocessable Entity (non-numeric values)
    - 500: Internal Server Error
    
    **Usage Notes:**
    - Both parameters are required
    - Values must be valid integers
    - Response is returned in JSON format
    """)
    
    if st.button("🚀 Try This Example"):
        st.session_state.example_clicked = True
        st.info("✨ Go to the 'Generate Docs' tab and use the example values shown above!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🚀 Powered by Azure OpenAI | 💡 Simple & Localized | 💾 No Database Required</p>
</div>
""", unsafe_allow_html=True)

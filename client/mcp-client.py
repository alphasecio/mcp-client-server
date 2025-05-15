import os, asyncio
import streamlit as st
import google.generativeai as genai
from fastmcp import Client
from fastmcp.client.transports import SSETransport, StreamableHttpTransport

# Initialise session state for client, tools and messages
if "client" not in st.session_state:
    st.session_state.client = None

if "tools" not in st.session_state:
    st.session_state.tools = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app config
st.set_page_config(page_title="MCP Demo", page_icon="🛡️", initial_sidebar_state="auto")

def normalize_url(url, transport_type):
    # Validate that the URL starts with http or https
    if not url.startswith(("http://", "https://")):
        st.error("URL must start with http:// or https://")
        st.stop()

    # Normalize trailing slashes for consistent checks
    url = url.rstrip("/")

    # Modify URL based on transport type
    if transport_type == "SSE":
        if not url.endswith("/sse"):
            url += "/sse"
    elif transport_type == "Streamable HTTP":
        if not (url.endswith("/mcp") or url.endswith("/mcp/")):
            url += "/mcp/"
        elif url.endswith("/mcp"):
            url += "/"

    return url

# App settings
with st.sidebar:
    st.title("🛡️ MCP Demo")
    st.subheader("⚙️ Settings")
    with st.container(border=True):
        if not os.environ.get("GOOGLE_API_KEY"):
            google_api_key = st.text_input("Google API Key", type="password", help="Get your API key [here](https://aistudio.google.com/apikey).")
        else:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
    
    with st.container(border=True):
        server_url = st.text_input("MCP Server URL").strip()
        transport_type = st.selectbox("MCP Transport", ("Streamable HTTP", "SSE"))
        connect = st.button(label="Connect")
        
        if connect:
            if not server_url.strip():
                st.error("Please provide the MCP Server URL.")
            else:
                try:
                    async def init_client_async():
                        try:
                            url = normalize_url(server_url, transport_type)
                            print(url)
                            if transport_type == "SSE":
                                transport = SSETransport(url)
                            elif transport_type == "Streamable HTTP":
                                transport = StreamableHttpTransport(url)
                            
                            async with Client(transport) as client:
                                tools = await client.list_tools()
                                return client, tools
                        except Exception as e:
                            st.error(f"Error during connection or tool listing: {e}")
                            return None, None

                    client, tools = asyncio.run(init_client_async())
                    
                    if client:
                        st.session_state.client = client
                        st.session_state.tools = tools
                    else:
                        st.session_state.client = None
                        st.session_state.tools = []
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Always display tools if they are in session_state
    if st.session_state.tools:
        st.write("🛠️ Tools Available")
        for tool in st.session_state.tools:
            with st.expander(f"🔧 {tool.name}", expanded=False):
                st.write(f"`{tool.description}`")
                st.write("Input Schema:")                        
                schema_props = tool.inputSchema.get("properties", {})
                if schema_props:
                    for prop, details in schema_props.items():
                        type_str = details.get("type", "unknown")
                        st.write(f"- `{prop}`: `{type_str}`")
                else:
                    st.write("_No input schema available._")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize Google GenAI client if key is provided
if google_api_key.strip():
    if "genai_client" not in st.session_state:
        genai.configure(api_key=google_api_key)
        st.session_state.genai_client = genai.GenerativeModel("gemini-2.0-flash")

# User-Assistant chat interaction
if prompt := st.chat_input("Ask anything"):
    if not google_api_key.strip():
        st.error("Please provide Google API key.")
        st.stop()
    else:
        try:
            # User prompt
            with st.chat_message("user"):
                st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

            # Build the prompt with tools context only if connected and tools are available
            if (st.session_state.client is not None and st.session_state.tools):
                tool_names = [tool.name for tool in st.session_state.tools]
                tools_context = f"\n\nAvailable tools on the MCP server: {', '.join(tool_names)}."
                full_prompt = prompt + tools_context
            else:
                full_prompt = prompt

            # Assistant response
            with st.chat_message("assistant"):
                response = st.session_state.genai_client.generate_content(full_prompt, stream=False)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Exception: {e}")

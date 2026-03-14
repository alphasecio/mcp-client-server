import os, json, asyncio, nest_asyncio
import streamlit as st
import google.genai as genai

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Patch asyncio to avoid "Event loop is closed" errors in Streamlit
nest_asyncio.apply()

# Initialise session state for connection config, tools, messages and access token
if "mcp_config" not in st.session_state:
    st.session_state.mcp_config = None
if "mcp_tools" not in st.session_state:
    st.session_state.mcp_tools = []
if "genai_client" not in st.session_state:
    st.session_state.genai_client = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "connection_error" not in st.session_state:
    st.session_state.connection_error = None
if "is_connected" not in st.session_state:
    st.session_state.is_connected = False

# Streamlit app configuration
st.set_page_config(page_title="MCP Chatbot", page_icon="💬", initial_sidebar_state="auto")

MODEL = "gemini-2.5-flash"

# Helper functions
def load_mcp_config():
    try:
        return json.loads(os.environ.get("MCP_SERVER_CONFIG", '{"mcpServers":{}}'))
    except Exception:
        return {"mcpServers": {}}

def normalize_url(url: str) -> str:
    """Ensure the MCP HTTP server URL is valid and normalized."""
    url = url.strip()
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    url = url.rstrip("/")
    if not (url.endswith("/mcp") or url.endswith("/mcp/")):
        url += "/mcp/"
    elif url.endswith("/mcp"):
        url += "/"
    return url

def create_transport(config, token=None):
    """Create transport with optional token."""
    auth_token = token if token else None
    return StreamableHttpTransport(config["url"], auth=auth_token)

async def test_connection_and_get_tools(transport):
    """Test connection and retrieve tools. Returns (tools, error)."""
    try:
        async with Client(transport) as client:
            tools = await client.list_tools()
            return tools, None
    except Exception as e:
        error_msg = str(e)
        # Check for common auth errors
        if "401" in error_msg or "Unauthorized" in error_msg:
            return None, "unauthorized"
        elif "403" in error_msg or "Forbidden" in error_msg:
            return None, "forbidden"
        elif "404" in error_msg or "Not Found" in error_msg:
            return None, "not_found"
        else:
            return None, error_msg

async def generate_response(prompt, mcp_config):
    if mcp_config and st.session_state.is_connected:
        try:
            transport = create_transport(mcp_config, st.session_state.access_token)
            async with Client(transport) as client:
                tools = [client.session]
                response = await st.session_state.genai_client.aio.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0,
                        tools=tools,
                    ),
                )
                return response
        except Exception as e:
            st.error(f"Error during Gemini generation with MCP client: {e}")
    
    try:
        response = await st.session_state.genai_client.aio.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=None,
            ),
        )
        return response
    except Exception as e:
        st.error(f"Error during Gemini generation: {e}")
        return None

# Sidebar settings
with st.sidebar:
    st.title("💬 MCP Chatbot")
    st.subheader("⚙️ Settings")
    
    # Google API Key
    if "GOOGLE_API_KEY" not in os.environ:
        with st.container(border=True):
            google_api_key = st.text_input("Google API Key", type="password", help="Get your API key [here](https://aistudio.google.com/apikey).")
    else:
        google_api_key = os.environ.get("GOOGLE_API_KEY")

    # Initialize Google GenAI client
    if google_api_key and google_api_key.strip() and not st.session_state.genai_client:
        try:
            st.session_state.genai_client = genai.Client(api_key=google_api_key)
        except Exception as e:
            st.error(f"Failed to initialise Gemini client: {e}")
    
    # MCP Server Configuration
    with st.container(border=True):
        config = load_mcp_config()
        server_keys = list(config["mcpServers"].keys()) + ["custom"]

        selected_key = st.selectbox("MCP Server", server_keys)

        default_url = st.session_state.mcp_config.get("url", "") if st.session_state.mcp_config else ""
    
        if selected_key != "custom":
            selected_server = config["mcpServers"][selected_key]
            server_url = st.text_input("MCP Server URL", value=selected_server["url"], disabled=True)
        else:
            server_url = st.text_input("MCP Server URL", value=default_url, placeholder="https://example.com/mcp/")
        
        # Access Token Input (always visible, but optional)
        token_value = st.text_input(
            "API Key / Access Token (optional)", 
            type="password",
            value=st.session_state.access_token,
            help="Required for protected MCP servers. Leave blank for public servers.",
            key="token_input"
        )
        
        # Update token in session state when changed
        if token_value != st.session_state.access_token:
            st.session_state.access_token = token_value
        
        # Connection status indicator
        if st.session_state.is_connected:
            st.success(f"✅ Connected to MCP server.")
        
        # Display connection errors
        if st.session_state.connection_error:
            if st.session_state.connection_error == "unauthorized":
                st.error("❌ **401 Unauthorized**: Please provide a valid API key or access token.")
            elif st.session_state.connection_error == "forbidden":
                st.error("❌ **403 Forbidden**: Access token is valid but lacks permissions.")
            elif st.session_state.connection_error == "not_found":
                st.error("❌ **404 Not Found**: MCP server endpoint not found. Check the URL.")
            else:
                st.error(f"❌ Connection error: {st.session_state.connection_error}")

        # Connect/Disconnect buttons
        col1, col2 = st.columns(2)
        with col1:
            connect = st.button(label="Connect", disabled=st.session_state.is_connected)
        with col2:
            disconnect = st.button(label="Disconnect", disabled=not st.session_state.is_connected)
        
        if disconnect:
            st.session_state.is_connected = False
            st.session_state.mcp_tools = []
            st.session_state.access_token = ""
            st.session_state.connection_error = None
            st.rerun()

        if connect:
            if not server_url.strip():
                st.session_state.connection_error = "MCP Server URL cannot be empty."
            else:
                try:
                    url = normalize_url(server_url)
                    test_config = {
                        "url": url,
                        "transport_type": "streamable-http"
                    }
    
                    # Test connection with current token
                    transport = create_transport(test_config, st.session_state.access_token)
                    tools, error = asyncio.run(test_connection_and_get_tools(transport))
    
                    if error:
                        # Connection failed
                        st.session_state.connection_error = error
                        st.session_state.is_connected = False
                        st.session_state.mcp_tools = []
                        st.rerun()
                    else:
                        # Connection successful
                        st.session_state.mcp_config = test_config
                        st.session_state.mcp_tools = tools
                        st.session_state.is_connected = True
                        st.session_state.connection_error = None
                        st.rerun()
    
                except Exception as e:
                    st.session_state.connection_error = str(e)
                    st.session_state.is_connected = False
                    st.session_state.mcp_tools = []
    
    # Display available tools once connected
    if st.session_state.is_connected and st.session_state.mcp_tools:
        st.subheader("🛠️ Tools Available")
        for tool in st.session_state.mcp_tools:
            with st.expander(f"🔧 {tool.name}", expanded=False):
                st.write(f"`{tool.description}`")
                st.write("**Input Schema:**")                        
                schema_props = tool.inputSchema.get("properties", {})
                if schema_props:
                    for prop, details in schema_props.items():
                        type_str = details.get("type", "unknown")
                        desc = details.get("description", "")
                        required = "required" if prop in tool.inputSchema.get("required", []) else "optional"
                        st.write(f"- `{prop}` ({type_str}, {required}): {desc}")
                else:
                    st.write("_No input schema available._")
    elif not st.session_state.is_connected:
        st.info("🔌 Not connected to MCP server.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User-Assistant chat interaction
if prompt := st.chat_input("Ask anything"):
    if not st.session_state.genai_client:
        st.error("Provide Google API key.")
        st.stop()
    
    # User prompt
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
            
    # Assistant response
    with st.chat_message("assistant"):
        ERROR_MSG = "Sorry, I couldn't generate a response. Please try again."
        try:
            enhanced_prompt = prompt
            if st.session_state.is_connected and st.session_state.mcp_tools:
                tool_names = [tool.name for tool in st.session_state.mcp_tools]
                enhanced_prompt += f"\n\nAvailable tools on the MCP server: {', '.join(tool_names)}."
            
            response = asyncio.run(generate_response(enhanced_prompt, st.session_state.mcp_config))
            
            if response and hasattr(response, 'text') and response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error(ERROR_MSG)
                st.session_state.messages.append({"role": "assistant", "content": ERROR_MSG})
 
        except Exception as e:
            st.error(f"Exception: {e}")
            st.session_state.messages.append({"role": "assistant", "content": ERROR_MSG})

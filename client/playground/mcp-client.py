import os, json, asyncio, nest_asyncio
import streamlit as st
import google.genai as genai

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Patch asyncio to avoid "Event loop is closed" errors in Streamlit
nest_asyncio.apply()

# Initialise session state for connection config, tools, messages and access token
if "mcp_config" not in st.session_state:
    st.session_state.mcp_config = {"url": "", "transport_type": "streamable-http"}
if "mcp_tools" not in st.session_state:
    st.session_state.mcp_tools = []
if "genai_client" not in st.session_state:
    st.session_state.genai_client = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "show_token_input" not in st.session_state:
    st.session_state.show_token_input = False

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

def create_transport(config):
    return StreamableHttpTransport(
        config["url"], 
        auth=st.session_state.access_token or None
    )

async def init_client_and_get_tools(transport):
    async with Client(transport) as client:
        tools = await client.list_tools()
        return tools

async def generate_response(prompt, mcp_config):
    if mcp_config:
        try:
            transport = create_transport(mcp_config)
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
    
    with st.container(border=True):
        config = load_mcp_config()
        server_keys = list(config["mcpServers"].keys()) + ["custom"]

        selected_key = st.selectbox("MCP Server", server_keys)

        current_cfg = st.session_state.mcp_config or {}
        default_url = current_cfg.get("url", "")
        default_transport = current_cfg.get("transport_type", "streamable-http")
    
        if selected_key != "custom":
            selected_server = config["mcpServers"][selected_key]
            server_url = st.text_input("MCP Server URL", value=selected_server["url"], disabled=True)
        else:
            server_url = st.text_input("MCP Server URL", value=default_url, placeholder="https://example.com/mcp/")
        
        current_config = {
            "url": server_url.strip(),
            "transport_type": default_transport
        }
        
        if st.session_state.show_token_input:
            token = st.text_input("Access Token", type="password", help="Paste your access token here.")
            if token:
                st.session_state.access_token = token
                st.session_state.show_token_input = False
                st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            connect = st.button(label="Connect")
        with col2:
            disconnect = st.button(label="Disconnect")

        if st.session_state.get("last_connect_error") == "unauthorized":
            st.warning("❌ Unauthorized (401). Please provide a valid access token.")
            st.session_state.last_connect_error = None
        
        if disconnect:
            st.session_state.show_token_input = False
            st.session_state.mcp_config = None
            st.session_state.mcp_tools = []
            st.session_state.access_token = ""
            st.rerun()

        if connect:
            if not server_url.strip():
                st.error("Provide MCP Server URL.")
            else:
                try:
                    url = normalize_url(current_config["url"])
                    st.session_state.mcp_config = {
                        "url": url,
                        "transport_type": "streamable-http"
                    }
    
                    transport = create_transport(st.session_state.mcp_config)
                    tools = asyncio.run(init_client_and_get_tools(transport))
    
                    if tools is not None:
                        st.session_state.mcp_tools = tools
                        st.session_state.show_token_input = False
                        st.rerun()
    
                except Exception as e:
                    if "401" in str(e):
                        st.session_state.show_token_input = True
                        st.session_state.last_connect_error = "unauthorized"
                        st.rerun()
                    else:
                        st.error(f"Connection error: {e}")
                        st.session_state.mcp_config = None
                        st.session_state.mcp_tools = []
    
    # Display available tools once connected
    if st.session_state.mcp_tools:
        st.subheader("🛠️ Tools Available")
        for tool in st.session_state.mcp_tools:
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
    else:
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
            if st.session_state.mcp_tools:
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

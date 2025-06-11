import os, json, asyncio, nest_asyncio
import streamlit as st
import google.genai as genai

from fastmcp import Client
from fastmcp.client.transports import SSETransport, StreamableHttpTransport

# Patch asyncio to avoid "Event loop is closed" errors in Streamlit
nest_asyncio.apply()

# Initialise session state for connection config, tools and messages
if "mcp_config" not in st.session_state:
    st.session_state.mcp_config = None

if "mcp_tools" not in st.session_state:
    st.session_state.mcp_tools = []

if "genai_client" not in st.session_state:
    st.session_state.genai_client = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app configuration
st.set_page_config(page_title="MCP Chatbot", page_icon="💬", initial_sidebar_state="auto")

MODEL = "gemini-2.0-flash"

# Helper functions
def load_mcp_config():
    try:
        return json.loads(os.environ.get("MCP_SERVER_CONFIG", '{"mcpServers":{}}'))
    except Exception as e:
        st.warning("Missing or invalid MCP config.")
        return {"mcpServers": {}}

def normalize_url(url: str, transport_type: str) -> str:
    # Validate that the URL starts with http or https
    if not url.startswith(("http://", "https://")):
        st.error("URL must start with http:// or https://")
        st.stop()

    # Normalize trailing slashes for consistent checks
    url = url.rstrip("/")

    # Modify URL based on transport type
    if transport_type == "sse":
        if not url.endswith("/sse"):
            url += "/sse"
    elif transport_type == "streamable-http":
        if not (url.endswith("/mcp") or url.endswith("/mcp/")):
            url += "/mcp/"
        elif url.endswith("/mcp"):
            url += "/"
    return url

def create_transport(config):
    if config["transport_type"] == "sse":
        return SSETransport(config["url"])
    else:
        return StreamableHttpTransport(config["url"])

async def init_client_and_get_tools(transport):
    try:
        async with Client(transport) as client:
            tools = await client.list_tools()
            return tools
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

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
    with st.container(border=True):
        if "GOOGLE_API_KEY" not in os.environ:
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

        if selected_key != "custom":
            selected_server = config["mcpServers"][selected_key]
            server_url = st.text_input("MCP Server URL", value=selected_server["url"], disabled=True)
            transport_type = st.selectbox("MCP Transport", ("streamable-http", "sse"),
                                        index=0 if selected_server["transport"].lower() == "streamable-http" else 1,
                                        disabled=True)
        else:
            default_url = st.session_state.mcp_config["url"] if st.session_state.mcp_config else ""
            default_transport = st.session_state.mcp_config["transport_type"] if st.session_state.mcp_config else "streamable-http"

            server_url = st.text_input("MCP Server URL", default_url)
            transport_type = st.selectbox("MCP Transport", ("streamable-http", "sse"),
                                        index=0 if default_transport == "streamable-http" else 1)
        
        current_config = {"url": server_url.strip(), "transport_type": transport_type}
        
        col1, col2 = st.columns(2)
        with col1:
            connect = st.button(label="Connect")
        with col2:
            disconnect = st.button(label="Disconnect")
        
        if disconnect:
            st.session_state.mcp_config = None
            st.session_state.mcp_tools = []
            st.rerun()

        if connect:
            if not server_url.strip():
                st.error("Provide MCP Server URL.")
            else:
                try:
                    url = normalize_url(current_config["url"], current_config["transport_type"])
                    transport = SSETransport(url) if current_config["transport_type"] == "sse" else StreamableHttpTransport(url)
                    tools = asyncio.run(init_client_and_get_tools(transport))

                    if tools is not None:
                        st.session_state.mcp_tools = tools
                        st.session_state.mcp_config = {"url": url, "transport_type": current_config["transport_type"]}
                        st.rerun()

                except Exception as e:
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

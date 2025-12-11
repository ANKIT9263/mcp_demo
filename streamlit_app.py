import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("MCP Chat Assistant")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "tool_calls" in message and message["tool_calls"]:
            with st.expander("Tool Calls"):
                for tool_call in message["tool_calls"]:
                    st.json(tool_call)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call client API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": prompt,
                        "conversation_history": st.session_state.conversation_history
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_message = data["response"]
                    tool_calls = data.get("tool_calls", [])

                    # Update conversation history
                    st.session_state.conversation_history = data["conversation_history"]

                    # Display response
                    st.markdown(assistant_message)

                    # Show tool calls if any
                    if tool_calls:
                        with st.expander("Tool Calls"):
                            for tool_call in tool_calls:
                                st.json(tool_call)

                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message,
                        "tool_calls": tool_calls
                    })
                else:
                    error_msg = f"Error: {response.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Sidebar
with st.sidebar:
    st.header("Chat Controls")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

    st.divider()

    st.header("Status")
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("API: Connected")
        else:
            st.error("API: Error")
    except:
        st.error("API: Disconnected")

    st.divider()

    st.header("Example Queries")
    st.markdown("""
    - Add 15 and 27
    - Greet Alice
    - What's the server info?
    - Show me the config
    """)

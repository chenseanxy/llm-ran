# Upstream: https://github.com/shiv248/Streamlit-x-LangGraph-Cookbooks/blob/master/tool_calling_via_events
# Upstream author: https://github.com/shiv248
# License: Unknown

import streamlit as st
import asyncio
from typing import Optional
import json

from langchain_core.messages import AIMessage, HumanMessage


def create_event_handler(graph_runnable):
    """
    Creates an event handler for processing events from the graph_runnable.

    Args:
        graph_runnable (StateGraph): The graph_runnable instance to be used for processing events.

    Returns:
        callable: A callable function that can be used to process events from the graph_runnable.
    """
    async def event_handler(messages, placeholder):
        return await invoke_our_graph(graph_runnable, messages, placeholder)

    return event_handler


def process_code(text: Optional[str]) -> Optional[str]:
    """
    Replaces special characters in the text for rendering in Streamlit.

    Args:
        text (str): The text to be processed.

    Returns:
        str: The processed text with special characters replaced.
    """
    if text is None:
        return None
    return text.replace("\n", "  \n")


def process_json(text: Optional[str]) -> Optional[str]:
    """
    Replaces special characters in the text for rendering in Streamlit.

    Args:
        text (str): The text to be processed.

    Returns:
        str: The processed text with special characters replaced.
    """
    if text is None:
        return None
    try:
        loaded = json.loads(text)
        return json.dumps(loaded, indent=2)
    except json.JSONDecodeError:
        return text


async def invoke_our_graph(graph_runnable, st_messages, st_placeholder):
    """
    Asynchronously processes a stream of events from the graph_runnable and updates the Streamlit interface.

    Args:
        graph_runnable (StateGraph): The graph_runnable instance to be used for processing events.
        st_messages (list): List of messages to be sent to the graph_runnable.
        st_placeholder (st.beta_container): Streamlit placeholder used to display updates and statuses.

    Returns:
        AIMessage: An AIMessage object containing the final aggregated text content from the events.
    """
    # Set up placeholders for displaying updates in the Streamlit app
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates
    final_text = ""  # Will store the accumulated text from the model's response

    # Stream events from the graph_runnable asynchronously
    async for event in graph_runnable.astream_events({"messages": st_messages}, version="v2"):
        kind = event["event"]  # Determine the type of event received

        if kind == "on_chat_model_stream":
            # The event corresponding to a stream of new content (tokens or chunks of text)
            addition = event["data"]["chunk"].content  # Extract the new content chunk
            final_text += addition  # Append the new content to the accumulated text
            if addition:
                token_placeholder.write(final_text)  # Update the st placeholder with the progressive response

        elif kind == "on_tool_start":
            # The event signals that a tool is about to be called
            with thoughts_placeholder:
                status_placeholder = st.empty()  # Placeholder to show the tool's status
                with status_placeholder.status("Calling Tool...", expanded=True) as s:
                    st.write("Called ", event['name'])  # Show which tool is being called
                    st.write("Tool input: ")
                    st.code(
                        body=process_code(event['data'].get('input', {}).get('code')),
                        language="python",
                    )  # Display the input data sent to the tool
                    st.write("Tool output: ")
                    output_placeholder = st.empty()  # Placeholder for tool output that will be updated later below
                    s.update(label="Completed Calling Tool!", expanded=False)  # Update the status once done

        elif kind == "on_tool_end":
            # The event signals the completion of a tool's execution
            with thoughts_placeholder:
                # We assume that `on_tool_end` comes after `on_tool_start`, meaning output_placeholder exists
                if 'output_placeholder' in locals():
                    output_placeholder.code(
                        body=process_json(event['data'].get('output').content),
                        language="json",
                    )  # Display the tool's output

    # Return the final aggregated message after all events have been processed
    return final_text


def main(graph):
    event_handler = create_event_handler(graph)

    st.markdown("""
## LLM-RAN
### Interactive Network Operations using Large Language Models in ORAN
    """)

    # Capture user input from chat input
    prompt = st.chat_input()

    # Initialize chat messages in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [AIMessage(content="How can I help you?")]
    
    if "containers" not in st.session_state:
        st.session_state["containers"] = []

    # Loop through all messages in the session state and render them as a chat on every st.refresh mech
    for msg in st.session_state.messages:
        # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
        # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)

    # Handle user input if provided
    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            # create a placeholder container for streaming and any other events to visually render here
            placeholder = st.container()
            response = asyncio.run(event_handler(st.session_state.messages, placeholder))
            st.session_state.messages.append(AIMessage(response))
            st.session_state.containers.append(placeholder)

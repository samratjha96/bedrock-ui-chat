import streamlit as st
import boto3
from typing import Iterator, Dict, List, Optional
from argon2 import PasswordHasher
import os
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name="us-west-2")


AVAILABLE_MODELS = [
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
]


def get_response(
    prompt: str, conversation_history: List[Dict], streaming: bool = True
) -> Iterator[tuple[str, str]] | tuple[str, str]:
    client = get_bedrock_client()
    model_id = st.session_state.selected_model

    CONVERSATION_WINDOW = 15  # Number of recent messages to include

    # Convert previous messages to API format
    api_messages = []
    for msg in conversation_history[-CONVERSATION_WINDOW:]:
        api_messages.append(
            {"role": msg["role"], "content": [{"text": msg["content"]}]}
        )

    # Add current prompt
    api_messages.append({"role": "user", "content": [{"text": prompt}]})

    request = {"messages": api_messages}

    # Add reasoning config only for Claude 3.7
    if model_id == "us.anthropic.claude-3-7-sonnet-20250219-v1:0":
        request["additionalModelRequestFields"] = {
            "reasoning_config": {"type": "enabled", "budget_tokens": 1024}
        }

    if streaming:
        response = client.converse_stream(modelId=model_id, **request)
        for chunk in response["stream"]:
            if "contentBlockDelta" in chunk:
                delta = chunk["contentBlockDelta"]["delta"]
                reasoning_text = ""
                response_text = ""

                if "reasoningContent" in delta:
                    if "text" in delta["reasoningContent"]:
                        reasoning_text = delta["reasoningContent"]["text"]
                if "text" in delta:
                    response_text = delta["text"]

                yield reasoning_text, response_text
    else:
        response = client.converse(modelId=model_id, **request)
        reasoning = response["output"]["message"]["content"][0]["reasoningContent"][
            "reasoningText"
        ]["text"]
        text = response["output"]["message"]["content"][1]["text"]
        return reasoning, text


# Thread management
def get_threads_dir() -> Path:
    threads_dir = Path(".bedrock-chat/threads")
    threads_dir.mkdir(parents=True, exist_ok=True)
    return threads_dir


def load_thread(thread_id: str) -> Optional[Dict]:
    thread_path = get_threads_dir() / f"{thread_id}.json"
    if thread_path.exists():
        return json.loads(thread_path.read_text())
    return None


def save_thread(thread_data: Dict) -> None:
    thread_path = get_threads_dir() / f"{thread_data['id']}.json"
    thread_path.write_text(json.dumps(thread_data, indent=2))


def list_threads() -> List[Dict]:
    threads = []
    for thread_path in get_threads_dir().glob("*.json"):
        thread_data = json.loads(thread_path.read_text())
        threads.append(
            {
                "id": thread_data["id"],
                "title": thread_data["title"],
                "created_at": thread_data["created_at"],
            }
        )
    return sorted(threads, key=lambda x: x["created_at"], reverse=True)


def create_thread() -> str:
    thread_id = str(uuid.uuid4())
    thread_data = {
        "id": thread_id,
        "created_at": datetime.now().isoformat(),
        "title": "New Chat",
        "model": st.session_state.selected_model,
        "messages": [],
    }
    save_thread(thread_data)
    return thread_id


# Security settings
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH", PasswordHasher().hash("change_me_immediately")
)

# Rate limiting
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 minutes in seconds
failed_attempts = defaultdict(list)


def is_rate_limited(username: str) -> tuple[bool, float]:
    current_time = time.time()
    # Clean up old attempts
    failed_attempts[username] = [
        t for t in failed_attempts[username] if current_time - t < LOCKOUT_TIME
    ]

    if len(failed_attempts[username]) >= MAX_ATTEMPTS:
        return True, LOCKOUT_TIME - (current_time - failed_attempts[username][0])
    return False, 0


def verify_password(password: str) -> bool:
    try:
        PasswordHasher().verify(ADMIN_PASSWORD_HASH, password)
        return True
    except:
        return False


# Streamlit UI
st.title("Bedrock Chat")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        is_limited, wait_time = is_rate_limited(username)
        if is_limited:
            st.error(
                f"Too many failed attempts. Please try again in {int(wait_time)} seconds."
            )
        elif username == ADMIN_USERNAME and verify_password(password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            failed_attempts[username].append(time.time())
            st.error("Invalid username or password")

if st.session_state.authenticated:
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    if "current_thread" not in st.session_state:
        st.session_state.current_thread = create_thread()

    # Sidebar for thread management
    with st.sidebar:
        if st.button("New Thread"):
            st.session_state.current_thread = create_thread()
            st.rerun()

        st.write("Past Conversations")
        for thread in list_threads():
            if st.button(thread["title"], key=thread["id"], use_container_width=True):
                st.session_state.current_thread = thread["id"]
                st.rerun()

    # Load current thread
    thread_data = load_thread(st.session_state.current_thread)
    if thread_data is None:
        st.error("Thread not found")
        st.session_state.current_thread = create_thread()
        st.rerun()

    messages = thread_data["messages"]

    # Model selector
    selected = st.selectbox(
        "Select Model",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model),
    )
    if selected != st.session_state.selected_model:
        st.session_state.selected_model = selected
        st.rerun()

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        messages.append(
            {"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}
        )
        # Update thread title if this is the first message
        if len(messages) == 1:
            thread_data["title"] = prompt[:30] + "..." if len(prompt) > 30 else prompt
        save_thread(thread_data)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Auto-expand thinking process for Claude 3.7
            thinking_expander = st.expander(
                "Thinking process",
                expanded=(
                    st.session_state.selected_model
                    == "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                ),
            )
            thinking_placeholder = thinking_expander.empty()
            message_placeholder = st.empty()
            thinking = ""
            full_response = ""

            for thinking_chunk, response_chunk in get_response(prompt, messages):
                if thinking_chunk:
                    thinking += thinking_chunk
                    thinking_placeholder.markdown(thinking + "▌")
                if response_chunk:
                    full_response += response_chunk
                    message_placeholder.markdown(full_response + "▌")

            thinking_placeholder.markdown(thinking)
            message_placeholder.markdown(full_response)

        messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "thinking": thinking
                if st.session_state.selected_model
                == "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                else "",
                "timestamp": datetime.now().isoformat(),
            }
        )
        save_thread(thread_data)

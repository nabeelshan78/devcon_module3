import streamlit as st
import tempfile
import os
import re 
from src.core.reasoning_engine import AdaptiveAgent
from src.utils.network import NetworkSentinel

# # 1. Page Config
# st.set_page_config(
#     page_title="Adaptive Agent Pro",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # 2. CSS (Keep existing)
# st.markdown("""
#     <style>
#     .stApp { background-color: #0E1117; color: #FFFFFF; }
#     [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363d; }
#     .stChatMessage { background-color: #1c2128 !important; border: 1px solid #30363d !important; border-radius: 10px !important; color: #FFFFFF !important; }
#     .stStatusWidget, .stExpander { background-color: #1c2128 !important; border: 1px solid #30363d !important; color: #FFFFFF !important; }
#     [data-testid="stMetricValue"] { color: #FFFFFF !important; }
#     </style>
# """, unsafe_allow_html=True)


# 1. Page Config
st.set_page_config(
    page_title="Adaptive Agent Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS (Updated for smaller metrics)
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363d; }
    
    /* Chat Bubbles */
    .stChatMessage { background-color: #1c2128 !important; border: 1px solid #30363d !important; border-radius: 10px !important; color: #FFFFFF !important; }
    
    /* Status Widgets */
    .stStatusWidget, .stExpander { background-color: #1c2128 !important; border: 1px solid #30363d !important; color: #FFFFFF !important; }
    
    /* --- METRIC RESIZING --- */
    /* Target the big number in st.metric */
    [data-testid="stMetricValue"] {
        font-size: 20px !important; /* Force smaller size */
        color: #00FF00 !important; /* Optional: Make it pop slightly */
    }
    
    /* Target the label above the number */
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #aaaaaa !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "agent" not in st.session_state:
    st.session_state.agent = AdaptiveAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar: Control Center
with st.sidebar:
    st.header("Control Center")
    st.markdown("---")
    
    st.write("### Network Sentinel")
    sentinel = NetworkSentinel()
    latency = sentinel.ping()
    auto_mode = sentinel.get_mode() # Get what the network thinks we should do
    
    col1, col2 = st.columns(2)
    col1.metric("Latency", f"{int(latency)}ms")
    col2.metric("Auto Mode", auto_mode.split('_')[0][:].upper())
    
    st.markdown("---")
    
    # --- NEW FEATURE: MANUAL OVERRIDE ---
    st.write("### Strategy Override")
    user_strategy = st.radio(
        "Select Reasoning Depth:",
        ["Auto (Network)", "Deep Reasoning", "Standard", "Fast Response"],
        index=0,
        help="Force a specific reasoning mode or let the network decide."
    )
    # ------------------------------------

    st.markdown("---")
    st.write("### Knowledge Base")
    uploaded_file = st.file_uploader("Upload PDF Context", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            st.session_state.agent.upload_document(tmp.name)
        st.success("Context Loaded")

# 4. Main UI Logic
st.markdown('# Adaptive Reasoning Agent')
st.caption("Mistral-powered agent with network-aware reasoning and native RAG.")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("thought"):
            with st.expander("Internal Thinking"):
                st.markdown(msg["thought"])
        st.markdown(msg["content"])
        
        if msg.get("file_path") and os.path.exists(msg["file_path"]):
            with open(msg["file_path"], "rb") as file:
                st.download_button(
                    label="📥 Download Generated Document",
                    data=file,
                    file_name=os.path.basename(msg["file_path"]),
                    mime="application/pdf",
                    key=f"dl_{msg['file_path']}"
                )

# 5. User Input and Agent Response
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.status("Agent is thinking...", expanded=True)
        
        with status_placeholder:
            placeholder = st.empty()
            full_response = ""
            
            # --- PASS USER STRATEGY HERE ---
            stream_gen = st.session_state.agent.execute_stream(prompt, user_strategy)
            # -------------------------------
            
            for chunk in stream_gen:
                if chunk.data.choices[0].delta.content:
                    content = chunk.data.choices[0].delta.content
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            
            # Sanitization Logic
            thought = ""
            final = full_response

            if "---" in full_response:
                parts = full_response.rsplit("---", 1) 
                thought = parts[0]
                final = parts[1]
            elif "[Polished Answer]" in full_response:
                parts = full_response.split("[Polished Answer]")
                thought = parts[0]
                final = parts[1]

            headers_to_strip = [
                "[Logic Summary]", "[Polished Answer]", "Strategy:", 
                "REASONING_MODE:", "---", "Final Answer:", "Answer:"
            ]
            
            for header in headers_to_strip:
                final = final.replace(header, "")
                thought = thought.replace(header, "")

            # Download Handler
            file_path = None
            download_match = re.search(r"\[\[DOWNLOAD:(.*?)\]\]", final)
            if download_match:
                file_path = download_match.group(1).strip()
                final = final.replace(download_match.group(0), "")

            status_placeholder.update(label="Reasoning Complete", state="complete", expanded=False)

        st.markdown(final.strip())
        
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as file:
                st.download_button(
                    label="📥 Download Generated Document",
                    data=file,
                    file_name=os.path.basename(file_path),
                    mime="application/pdf"
                )
        
        if thought.strip():
            with st.expander("🔍 View Internal Logic"):
                st.info(thought.strip())

        st.session_state.messages.append({
            "role": "assistant", 
            "content": final.strip(), 
            "thought": thought.strip(),
            "file_path": file_path 
        })

# import streamlit as st
# import tempfile
# import os
# import re  # <--- Added for parsing download tags
# from src.core.reasoning_engine import AdaptiveAgent
# from src.utils.network import NetworkSentinel

# # 1. Page Config
# st.set_page_config(
#     page_title="Adaptive Agent Pro",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # 2. Corrected CSS for Dark Theme Consistency
# st.markdown("""
#     <style>
#     /* Main Background */
#     .stApp {
#         background-color: #0E1117;
#         color: #FFFFFF;
#     }
    
#     /* Sidebar Background */
#     [data-testid="stSidebar"] {
#         background-color: #161B22;
#         border-right: 1px solid #30363d;
#     }

#     /* REMOVE WHITE BACKGROUND FROM CHAT BUBBLES */
#     .stChatMessage {
#         background-color: #1c2128 !important; /* Dark grey instead of white */
#         border: 1px solid #30363d !important;
#         border-radius: 10px !important;
#         color: #FFFFFF !important;
#     }

#     /* REMOVE WHITE BACKGROUND FROM STATUS/EXPANDERS */
#     .stStatusWidget, .stExpander {
#         background-color: #1c2128 !important;
#         border: 1px solid #30363d !important;
#         color: #FFFFFF !important;
#     }
    
#     /* Ensure metric text is white */
#     [data-testid="stMetricValue"] {
#         color: #FFFFFF !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Session State Initialization
# if "agent" not in st.session_state:
#     st.session_state.agent = AdaptiveAgent()
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # 3. Sidebar: Control Center
# with st.sidebar:
#     st.header("Control Center")
#     st.markdown("---")
    
#     st.write("### Network Sentinel")
#     sentinel = NetworkSentinel()
#     latency = sentinel.ping()
#     mode = sentinel.get_mode()
    
#     col1, col2 = st.columns(2)
#     col1.metric("Latency", f"{int(latency)}ms")
#     # size of text
#     col2.metric("Mode", mode.split('_')[0][:4].upper() + "...")
    
#     st.markdown("---")
#     st.write("### Knowledge Base")
#     uploaded_file = st.file_uploader("Upload PDF Context", type=["pdf"], label_visibility="collapsed")
    
#     if uploaded_file:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#             tmp.write(uploaded_file.getvalue())
#             st.session_state.agent.upload_document(tmp.name)
#         st.success("Context Loaded")

# # 4. Main UI Logic
# st.markdown('# Adaptive Reasoning Agent')
# st.caption("Mistral-powered agent with network-aware reasoning and native RAG.")

# # Display History
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         if msg.get("thought"):
#             with st.expander("Internal Thinking"):
#                 st.markdown(msg["thought"])
        
#         st.markdown(msg["content"])
        
#         # Check if this message has an attached file to download
#         if msg.get("file_path") and os.path.exists(msg["file_path"]):
#             with open(msg["file_path"], "rb") as file:
#                 st.download_button(
#                     label="📥 Download Generated Document",
#                     data=file,
#                     file_name=os.path.basename(msg["file_path"]),
#                     mime="application/pdf",
#                     key=f"dl_{msg['file_path']}" # Unique key for history buttons
#                 )

# # 5. User Input and Agent Response
# if prompt := st.chat_input("Ask a question..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         status_placeholder = st.status("Agent is thinking...", expanded=True)
        
#         with status_placeholder:
#             placeholder = st.empty()
#             full_response = ""
#             stream_gen = st.session_state.agent.execute_stream(prompt)
            
#             for chunk in stream_gen:
#                 if chunk.data.choices[0].delta.content:
#                     content = chunk.data.choices[0].delta.content
#                     full_response += content
#                     placeholder.markdown(full_response + "▌")
            
#             # --- ADVANCED SANITIZATION LOGIC ---
#             thought = ""
#             final = full_response

#             # 1. Split by the primary competition delimiter
#             if "---" in full_response:
#                 parts = full_response.rsplit("---", 1) 
#                 thought = parts[0]
#                 final = parts[1]
            
#             # 2. If the model used headers instead of delimiters
#             elif "[Polished Answer]" in full_response:
#                 parts = full_response.split("[Polished Answer]")
#                 thought = parts[0]
#                 final = parts[1]

#             # 3. CLEANUP: Strip known "System" headers from the UI display
#             headers_to_strip = [
#                 "[Logic Summary]", "[Polished Answer]", "Strategy:", 
#                 "REASONING_MODE:", "---", "Final Answer:", "Answer:"
#             ]
            
#             for header in headers_to_strip:
#                 final = final.replace(header, "")
#                 thought = thought.replace(header, "")

#             # 4. DOWNLOAD HANDLER (New Feature)
#             # Regex to find [[DOWNLOAD:path/to/file.pdf]]
#             file_path = None
#             download_match = re.search(r"\[\[DOWNLOAD:(.*?)\]\]", final)
            
#             if download_match:
#                 file_path = download_match.group(1).strip()
#                 # Remove the tag from the displayed text so it looks clean
#                 final = final.replace(download_match.group(0), "")

#             status_placeholder.update(label="Reasoning Complete", state="complete", expanded=False)

#         # Show the sanitized final answer
#         st.markdown(final.strip())
        
#         # Show the Download Button immediately if a file was generated
#         if file_path and os.path.exists(file_path):
#             with open(file_path, "rb") as file:
#                 st.download_button(
#                     label="📥 Download Generated Document",
#                     data=file,
#                     file_name=os.path.basename(file_path),
#                     mime="application/pdf"
#                 )
        
#         # Show the sanitized thought trace
#         if thought.strip():
#             with st.expander("🔍 View Internal Logic"):
#                 st.info(thought.strip())

#         # Save to history (including file_path if it exists)
#         st.session_state.messages.append({
#             "role": "assistant", 
#             "content": final.strip(), 
#             "thought": thought.strip(),
#             "file_path": file_path  # Save path so button persists on reload
#         })

# # import streamlit as st
# # import tempfile
# # import os
# # from src.core.reasoning_engine import AdaptiveAgent
# # from src.utils.network import NetworkSentinel

# # # 1. Page Config
# # st.set_page_config(
# #     page_title="Adaptive Agent Pro",
# #     page_icon="",
# #     layout="wide",
# #     initial_sidebar_state="expanded"
# # )

# # # 2. Corrected CSS for Dark Theme Consistency
# # st.markdown("""
# #     <style>
# #     /* Main Background */
# #     .stApp {
# #         background-color: #0E1117;
# #         color: #FFFFFF;
# #     }
    
# #     /* Sidebar Background */
# #     [data-testid="stSidebar"] {
# #         background-color: #161B22;
# #         border-right: 1px solid #30363d;
# #     }

# #     /* REMOVE WHITE BACKGROUND FROM CHAT BUBBLES */
# #     .stChatMessage {
# #         background-color: #1c2128 !important; /* Dark grey instead of white */
# #         border: 1px solid #30363d !important;
# #         border-radius: 10px !important;
# #         color: #FFFFFF !important;
# #     }

# #     /* REMOVE WHITE BACKGROUND FROM STATUS/EXPANDERS */
# #     .stStatusWidget, .stExpander {
# #         background-color: #1c2128 !important;
# #         border: 1px solid #30363d !important;
# #         color: #FFFFFF !important;
# #     }
    
# #     /* Ensure metric text is white */
# #     [data-testid="stMetricValue"] {
# #         color: #FFFFFF !important;
# #     }
# #     </style>
# # """, unsafe_allow_html=True)

# # # Session State Initialization
# # if "agent" not in st.session_state:
# #     st.session_state.agent = AdaptiveAgent()
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []

# # # 3. Sidebar: Control Center
# # with st.sidebar:
# #     st.header("Control Center")
# #     st.markdown("---")
    
# #     st.write("### Network Sentinel")
# #     sentinel = NetworkSentinel()
# #     latency = sentinel.ping()
# #     mode = sentinel.get_mode()
    
# #     col1, col2 = st.columns(2)
# #     col1.metric("Latency", f"{int(latency)}ms")
# #     col2.metric("Mode", mode.split('_')[0][:4].upper() + "...")
    
# #     st.markdown("---")
# #     st.write("### Knowledge Base")
# #     uploaded_file = st.file_uploader("Upload PDF Context", type=["pdf"], label_visibility="collapsed")
    
# #     if uploaded_file:
# #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
# #             tmp.write(uploaded_file.getvalue())
# #             st.session_state.agent.upload_document(tmp.name)
# #         st.success("Context Loaded")

# # # 4. Main UI Logic
# # st.markdown('# Adaptive Reasoning Agent')
# # st.caption("Mistral-powered agent with network-aware reasoning and native RAG.")

# # # Display History
# # for msg in st.session_state.messages:
# #     with st.chat_message(msg["role"]):
# #         if msg.get("thought"):
# #             with st.expander("Internal Thinking"):
# #                 st.markdown(msg["thought"])
# #         st.markdown(msg["content"])



# # # 5. User Input and Agent Response
# # if prompt := st.chat_input("Ask a question..."):
# #     st.session_state.messages.append({"role": "user", "content": prompt})
# #     with st.chat_message("user"):
# #         st.markdown(prompt)

# #     with st.chat_message("assistant"):
# #         status_placeholder = st.status("Agent is thinking...", expanded=True)
        
# #         with status_placeholder:
# #             placeholder = st.empty()
# #             full_response = ""
# #             stream_gen = st.session_state.agent.execute_stream(prompt)
            
# #             for chunk in stream_gen:
# #                 if chunk.data.choices[0].delta.content:
# #                     content = chunk.data.choices[0].delta.content
# #                     full_response += content
# #                     placeholder.markdown(full_response + "▌")
            
# #             # --- ADVANCED SANITIZATION LOGIC ---
# #             thought = ""
# #             final = full_response

# #             # 1. Split by the primary competition delimiter
# #             if "---" in full_response:
# #                 # We take the LAST part as the answer, and everything before as logic
# #                 parts = full_response.rsplit("---", 1) 
# #                 thought = parts[0]
# #                 final = parts[1]
            
# #             # 2. If the model used headers instead of delimiters
# #             elif "[Polished Answer]" in full_response:
# #                 parts = full_response.split("[Polished Answer]")
# #                 thought = parts[0]
# #                 final = parts[1]

# #             # 3. CLEANUP: Strip known "System" headers from the UI display
# #             headers_to_strip = [
# #                 "[Logic Summary]", "[Polished Answer]", "Strategy:", 
# #                 "REASONING_MODE:", "---", "Final Answer:", "Answer:"
# #             ]
            
# #             for header in headers_to_strip:
# #                 final = final.replace(header, "")
# #                 thought = thought.replace(header, "")

# #             status_placeholder.update(label="Reasoning Complete", state="complete", expanded=False)

# #         # Show the sanitized final answer
# #         st.markdown(final.strip())
        
# #         # Show the sanitized thought trace
# #         if thought.strip():
# #             with st.expander("🔍 View Internal Logic"):
# #                 st.info(thought.strip())

# #         st.session_state.messages.append({
# #             "role": "assistant", 
# #             "content": final.strip(), 
# #             "thought": thought.strip()
# #         })
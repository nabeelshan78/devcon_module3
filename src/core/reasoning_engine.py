from mistralai import Mistral
from src.utils.network import NetworkSentinel
from src.tools.native_rag import NativeRAG
from src.tools.document_tool import DocumentTool
from src.tools.web_tool import WebSearchTool 
from config import MISTRAL_API_KEY
import datetime

class AdaptiveAgent:
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.sentinel = NetworkSentinel()
        self.rag = NativeRAG()
        self.docs = DocumentTool()
        self.web = WebSearchTool() 
        self.has_context = False

    def upload_document(self, file_path):
        """Standard RAG ingestion logic."""
        self.rag.ingest_pdf(file_path)
        self.has_context = True
    
    def execute_stream(self, user_query, override_mode="Auto (Network)"):
        """
        THE COMPETITION CORE:
        1. Checks User Override vs Network Sentinel.
        2. Detects Intent (Cognitive Routing).
        3. Throttles Tools (Social Intelligence).
        4. Adjusts Reasoning Framework.
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # --- 1. Mode Selection Logic ---
        # If user chooses Auto, ask Sentinel. Otherwise, force user choice.
        if "Deep Reasoning" in override_mode:
            mode = "DEEP_REASONING"
        elif "Standard" in override_mode:
            mode = "STANDARD"
        elif "Fast Response" in override_mode:
            mode = "FAST_RESPONSE"
        else:
            # Default to Network Sentinel
            mode = self.sentinel.get_mode()
        
        # --- 2. Cognitive Intent Routing ---
        greetings = ["hello", "hi", "hey", "assalam", "yo", "greeting"]
        is_social = any(g in user_query.lower().split() for g in greetings)

        print(f"[AGENT] Social: {is_social} | Selected Mode: {mode} (User: {override_mode})")

        intent_response = "NONE"
        if not is_social:
            router_prompt = f"""
            You are an intent classification system.
            Classify the QUERY into exactly ONE category:

            WEB  -> Real-time info (news, weather, stocks).
            RAG  -> Private documents/knowledge base.
            DOC  -> Request to create/generate/download a file (PDF, Excel, Word).
            NONE -> General knowledge.

            STRICT RULES: Output ONLY one word: WEB, RAG, DOC, or NONE.

            QUERY: {user_query}
            """

            intent_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": router_prompt}]
            ).choices[0].message.content.upper()

        print(f"[ROUTER] Intent Detected: {intent_response}")

        context_block = ""
        
        # --- 3. Dynamic Strategy Selection ---
        # Social queries always override to STANDARD to avoid over-engineering "Hi"
        effective_mode = "STANDARD" if is_social else mode
        
        # Select Model based on Mode
        model = "mistral-large-latest" if effective_mode == "DEEP_REASONING" else "mistral-small-latest"
        print(f"[AGENT] Effective Mode: {effective_mode} | Model: {model}")

        # --- 4. Strategic Tool Execution ---
        if not is_social:
            if "WEB" in intent_response or any(w in user_query.lower() for w in ["now", "today", "weather"]):
                web_data = self.web.search(user_query, mode=effective_mode)
                context_block += f"\n[LATEST WEB DATA]:\n{web_data}\n"
            
            if "RAG" in intent_response or self.has_context:
                retrieved_text = self.rag.retrieve(user_query)
                context_block += f"\n[DOCUMENT CONTEXT]:\n{retrieved_text}\n"
            
            if "DOC" in intent_response:
                return self._handle_doc_tool(user_query)

        # Framing the 'How' vs 'What'
        prompt = self._get_adaptive_prompt(effective_mode, user_query, context_block, now)
        
        # --- 5. Tool-Specific Fallbacks ---
        if "save" in user_query.lower() and ("pdf" in user_query.lower() or "excel" in user_query.lower() or "word" in user_query.lower()):
            return self._handle_doc_tool(user_query)

        # --- 6. Return Generator ---
        return self.client.chat.stream(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

    def _get_adaptive_prompt(self, mode, query, context, time):
        """
        MASTER-LEVEL ADAPTIVE REASONING CONTROLLER
        Controls reasoning depth while enforcing strict grounding hierarchy.
        """
        grounding = f"""
    SYSTEM_METADATA:
    - SYSTEM_TIME: {time}

    GROUNDING_RULES:
    1. AVAILABLE_CONTEXT is the highest authority.
    2. If AVAILABLE_CONTEXT exists, prioritize it over prior knowledge.
    3. If context conflicts with prior knowledge, trust context.
    4. If insufficient data, explicitly state uncertainty.
    5. Do NOT fabricate missing details.
    
    INPUTS:
    - AVAILABLE_CONTEXT: {context if context else "None"}
    - USER_QUERY: {query}
    """

        if mode == "DEEP_REASONING":
            framework = """
    REASONING_MODE: ANALYTICAL (High Deliberation)

    INTERNAL_PROCESS:
    1. Decompose the problem into core components.
    2. Extract verifiable facts from context and cross-reference.
    3. Identify and challenge underlying assumptions.
    4. Check for logical fallacies or inconsistencies.
    5. Synthesize a comprehensive, evidence-backed conclusion.

    OUTPUT_REQUIREMENTS:
    - Provide a structured, deeply detailed answer.
    - Use bullet points for clarity where complex.
    - Do NOT expose internal reasoning steps in the final output.
    """
        elif mode == "STANDARD":
            framework = """
    REASONING_MODE: STRUCTURED (Balanced)

    INTERNAL_PROCESS:
    - Identify key facts relevant to the user's intent.
    - Connect facts directly to the query.
    - Filter out tangential information.

    OUTPUT_REQUIREMENTS:
    - Clear, concise, and professional explanation.
    - Direct final answer with moderate detail.
    """
        else:  # FAST_RESPONSE
            framework = """
    REASONING_MODE: HEURISTIC (Low Latency)

    INTERNAL_PROCESS:
    - Identify the single most likely answer immediately.
    - Skip secondary analysis or "nice-to-know" details.
    - Focus purely on the "What" and "How".

    OUTPUT_REQUIREMENTS:
    - Extremely concise answer (TL;DR style).
    - No fluff. No extended explanation unless critical for safety.
    """
        return f"{grounding}\n{framework}"
   
    # def _get_adaptive_prompt(self, mode, query, context, time):
    #     """
    #     MASTER-LEVEL ADAPTIVE REASONING CONTROLLER
    #     """
    #     grounding = f"""
    # SYSTEM_METADATA:
    # - SYSTEM_TIME: {time}

    # GROUNDING_RULES:
    # 1. AVAILABLE_CONTEXT is the highest authority.
    # 2. If AVAILABLE_CONTEXT exists, prioritize it over prior knowledge.
    # 3. If context conflicts with prior knowledge, trust context.
    # 4. If insufficient data, explicitly state uncertainty.
    # 5. Do NOT fabricate missing details.

    # INPUTS:
    # - AVAILABLE_CONTEXT: {context if context else "None"}
    # - USER_QUERY: {query}
    # """

    #     if mode == "DEEP_REASONING":
    #         framework = """
    # REASONING_MODE: ANALYTICAL (High Deliberation)

    # INTERNAL_PROCESS:
    # 1. Decompose the problem.
    # 2. Extract verifiable facts from context.
    # 3. Identify assumptions (if any).
    # 4. Cross-check for logical consistency.
    # 5. Synthesize a grounded conclusion.

    # OUTPUT_REQUIREMENTS:
    # - Provide a structured, logically organized answer.
    # - Do NOT expose hidden reasoning steps.
    # - Clearly separate explanation and conclusion.
    # """
    #     elif mode == "STANDARD":
    #         framework = """
    # REASONING_MODE: STRUCTURED (Balanced)

    # INTERNAL_PROCESS:
    # - Identify key facts.
    # - Connect them directly to the query.
    # - Avoid unnecessary elaboration.

    # OUTPUT_REQUIREMENTS:
    # - Clear and concise explanation.
    # - Direct final answer.
    # """
    #     else:  # FAST_RESPONSE
    #         framework = """
    # REASONING_MODE: HEURISTIC (Low Latency)

    # INTERNAL_PROCESS:
    # - Use strongest available signal.
    # - Prefer brevity over depth.
    # - Skip secondary analysis.

    # OUTPUT_REQUIREMENTS:
    # - Concise answer.
    # - No extended explanation unless critical.
    # """
    #     return f"{grounding}\n{framework}"

    def _handle_doc_tool(self, query):
        """
        Smartly generates PDF, WORD, or EXCEL based on user query keywords.
        """
        query_lower = query.lower()
        
        # 1. Determine File Type and Prompt
        if "excel" in query_lower or "spreadsheet" in query_lower or "csv" in query_lower:
            file_type = "EXCEL"
            prompt_instruction = (
                "You are a Data Generator. Output ONLY data in CSV format (comma-separated).\n"
                "Do not use markdown blocks. Just the raw data.\n"
                "Example:\nName, Age, Role\nAlice, 25, Engineer\n"
                "Generate data for: "
            )
        elif "word" in query_lower or "docx" in query_lower:
            file_type = "WORD"
            prompt_instruction = (
                "You are a Document Generator. Output content for a Word Document.\n"
                "Use '# ' for Titles, '## ' for Headings, '* ' for bullets.\n"
                "Write about: "
            )
        else:
            file_type = "PDF" # Default
            prompt_instruction = (
                "You are a PDF Generator. Output content in strict format:\n"
                "- Use '# ' for Main Titles.\n"
                "- Use '## ' for Section Headings.\n"
                "- Use '* ' for bullet points.\n"
                "- Do NOT use bolding symbols like ** inside the text.\n"
                "Write a comprehensive summary about: "
            )

        print(f"[TOOL] 📄 Generating {file_type} content for: {query}")
        
        # 2. Generate Content
        content = self.client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt_instruction + query}]
        ).choices[0].message.content
        
        # 3. Create the physical file
        if file_type == "EXCEL":
            path = self.docs.create_excel(content)
        elif file_type == "WORD":
            path = self.docs.create_word(content)
        else:
            path = self.docs.create_pdf(content)
        
        # 4. Yield the response with the HIDDEN TAG [[DOWNLOAD:path]]
        class ToolChunk:
            def __init__(self, text):
                self.data = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'delta': type('obj', (object,), {'content': text})()
                    })()]
                })()

        yield ToolChunk(f"I have generated your {file_type} document.\n\n[[DOWNLOAD:{path}]]")

# from mistralai import Mistral
# from src.utils.network import NetworkSentinel
# from src.tools.native_rag import NativeRAG
# from src.tools.document_tool import DocumentTool
# from src.tools.web_tool import WebSearchTool 
# from config import MISTRAL_API_KEY
# import datetime

# class AdaptiveAgent:
#     def __init__(self):
#         self.client = Mistral(api_key=MISTRAL_API_KEY)
#         self.sentinel = NetworkSentinel()
#         self.rag = NativeRAG()
#         self.docs = DocumentTool()
#         self.web = WebSearchTool() 
#         self.has_context = False

#     def upload_document(self, file_path):
#         """Standard RAG ingestion logic."""
#         self.rag.ingest_pdf(file_path)
#         self.has_context = True
    
#     def execute_stream(self, user_query):
#         """
#         THE COMPETITION CORE:
#         1. Senses Network (Sentinel).
#         2. Detects Intent (Cognitive Routing).
#         3. Throttles Tools (Social Intelligence).
#         4. Adjusts Reasoning Framework (System 1 vs System 2).
#         """
#         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         mode = self.sentinel.get_mode()
        
#         # --- 1. Cognitive Intent Routing ---
#         greetings = ["hello", "hi", "hey", "assalam", "yo", "greeting"]
#         is_social = any(g in user_query.lower().split() for g in greetings)

#         print(f"[AGENT] Social: {is_social} | Mode: {mode}")

#         intent_response = "NONE"
#         if not is_social:
#             router_prompt = f"""
#             You are an intent classification system.
#             Classify the QUERY into exactly ONE category:

#             WEB  -> Real-time info (news, weather, stocks).
#             RAG  -> Private documents/knowledge base.
#             DOC  -> Request to create/generate/download a file (PDF, Excel, Word).
#             NONE -> General knowledge.

#             STRICT RULES: Output ONLY one word: WEB, RAG, DOC, or NONE.

#             QUERY: {user_query}
#             """

#             intent_response = self.client.chat.complete(
#                 model="mistral-small-latest",
#                 messages=[{"role": "user", "content": router_prompt}]
#             ).choices[0].message.content.upper()

        
#         print(f"[ROUTER] Intent Detected: {intent_response}")

#         context_block = ""
        
#         # --- 2. Dynamic Strategy Selection ---
#         effective_mode = "STANDARD" if is_social else mode
#         model = "mistral-large-latest" if effective_mode == "DEEP_REASONING" else "mistral-small-latest"
#         print(f"[AGENT] Effective Mode: {effective_mode} | Model: {model}")

#         # --- 3. Strategic Tool Execution ---
#         if not is_social:
#             if "WEB" in intent_response or any(w in user_query.lower() for w in ["now", "today", "weather"]):
#                 # NEW: Pass the effective mode to control depth
#                 web_data = self.web.search(user_query, mode=effective_mode)
#                 context_block += f"\n[LATEST WEB DATA]:\n{web_data}\n"
            
#             if "RAG" in intent_response or self.has_context:
#                 retrieved_text = self.rag.retrieve(user_query)
#                 context_block += f"\n[DOCUMENT CONTEXT]:\n{retrieved_text}\n"
            
#             if "DOC" in intent_response:
#                 # Use the new generalized handler
#                 return self._handle_doc_tool(user_query)

#         # Framing the 'How' vs 'What'
#         prompt = self._get_adaptive_prompt(effective_mode, user_query, context_block, now)
        
#         # --- 4. Tool-Specific Fallbacks ---
#         if "save" in user_query.lower() and ("pdf" in user_query.lower() or "excel" in user_query.lower() or "word" in user_query.lower()):
#             return self._handle_doc_tool(user_query)

#         # --- 5. Return Generator ---
#         return self.client.chat.stream(
#             model=model,
#             messages=[{"role": "user", "content": prompt}]
#         )

#     def _get_adaptive_prompt(self, mode, query, context, time):
#         """
#         MASTER-LEVEL ADAPTIVE REASONING CONTROLLER
#         """
#         grounding = f"""
#     SYSTEM_METADATA:
#     - SYSTEM_TIME: {time}

#     GROUNDING_RULES:
#     1. AVAILABLE_CONTEXT is the highest authority.
#     2. If AVAILABLE_CONTEXT exists, prioritize it over prior knowledge.
#     3. If context conflicts with prior knowledge, trust context.
#     4. If insufficient data, explicitly state uncertainty.
#     5. Do NOT fabricate missing details.

#     INPUTS:
#     - AVAILABLE_CONTEXT: {context if context else "None"}
#     - USER_QUERY: {query}
#     """

#         if mode == "DEEP_REASONING":
#             framework = """
#     REASONING_MODE: ANALYTICAL (High Deliberation)

#     INTERNAL_PROCESS:
#     1. Decompose the problem.
#     2. Extract verifiable facts from context.
#     3. Identify assumptions (if any).
#     4. Cross-check for logical consistency.
#     5. Synthesize a grounded conclusion.

#     OUTPUT_REQUIREMENTS:
#     - Provide a structured, logically organized answer.
#     - Do NOT expose hidden reasoning steps.
#     - Clearly separate explanation and conclusion.
#     """
#         elif mode == "STANDARD":
#             framework = """
#     REASONING_MODE: STRUCTURED (Balanced)

#     INTERNAL_PROCESS:
#     - Identify key facts.
#     - Connect them directly to the query.
#     - Avoid unnecessary elaboration.

#     OUTPUT_REQUIREMENTS:
#     - Clear and concise explanation.
#     - Direct final answer.
#     """
#         else:  # FAST_RESPONSE
#             framework = """
#     REASONING_MODE: HEURISTIC (Low Latency)

#     INTERNAL_PROCESS:
#     - Use strongest available signal.
#     - Prefer brevity over depth.
#     - Skip secondary analysis.

#     OUTPUT_REQUIREMENTS:
#     - Concise answer.
#     - No extended explanation unless critical.
#     """
#         return f"{grounding}\n{framework}"

#     def _handle_doc_tool(self, query):
#         """
#         Smartly generates PDF, WORD, or EXCEL based on user query keywords.
#         """
#         query_lower = query.lower()
        
#         # 1. Determine File Type and Prompt
#         if "excel" in query_lower or "spreadsheet" in query_lower or "csv" in query_lower:
#             file_type = "EXCEL"
#             prompt_instruction = (
#                 "You are a Data Generator. Output ONLY data in CSV format (comma-separated).\n"
#                 "Do not use markdown blocks. Just the raw data.\n"
#                 "Example:\nName, Age, Role\nAlice, 25, Engineer\n"
#                 "Generate data for: "
#             )
#         elif "word" in query_lower or "docx" in query_lower:
#             file_type = "WORD"
#             prompt_instruction = (
#                 "You are a Document Generator. Output content for a Word Document.\n"
#                 "Use '# ' for Titles, '## ' for Headings, '* ' for bullets.\n"
#                 "Write about: "
#             )
#         else:
#             file_type = "PDF" # Default
#             prompt_instruction = (
#                 "You are a PDF Generator. Output content in strict format:\n"
#                 "- Use '# ' for Main Titles.\n"
#                 "- Use '## ' for Section Headings.\n"
#                 "- Use '* ' for bullet points.\n"
#                 "- Do NOT use bolding symbols like ** inside the text.\n"
#                 "Write a comprehensive summary about: "
#             )

#         print(f"[TOOL] 📄 Generating {file_type} content for: {query}")
        
#         # 2. Generate Content
#         content = self.client.chat.complete(
#             model="mistral-large-latest",
#             messages=[{"role": "user", "content": prompt_instruction + query}]
#         ).choices[0].message.content
        
#         # 3. Create the physical file
#         if file_type == "EXCEL":
#             path = self.docs.create_excel(content)
#         elif file_type == "WORD":
#             path = self.docs.create_word(content)
#         else:
#             path = self.docs.create_pdf(content)
        
#         # 4. Yield the response with the HIDDEN TAG [[DOWNLOAD:path]]
#         # Create a mock chunk object to satisfy the stream structure
#         class ToolChunk:
#             def __init__(self, text):
#                 self.data = type('obj', (object,), {
#                     'choices': [type('obj', (object,), {
#                         'delta': type('obj', (object,), {'content': text})()
#                     })()]
#                 })()

#         yield ToolChunk(f"I have generated your {file_type} document.\n\n[[DOWNLOAD:{path}]]")

# # from mistralai import Mistral
# # from src.utils.network import NetworkSentinel
# # from src.tools.native_rag import NativeRAG
# # from src.tools.document_tool import DocumentTool
# # from src.tools.web_tool import WebSearchTool 
# # from config import MISTRAL_API_KEY
# # import datetime

# # class AdaptiveAgent:
# #     def __init__(self):
# #         self.client = Mistral(api_key=MISTRAL_API_KEY)
# #         self.sentinel = NetworkSentinel()
# #         self.rag = NativeRAG()
# #         self.docs = DocumentTool()
# #         self.web = WebSearchTool() 
# #         self.has_context = False

# #     def upload_document(self, file_path):
# #         """Standard RAG ingestion logic."""
# #         self.rag.ingest_pdf(file_path)
# #         self.has_context = True
    
# #     def execute_stream(self, user_query):
# #         """
# #         THE COMPETITION CORE:
# #         1. Senses Network (Sentinel).
# #         2. Detects Intent (Cognitive Routing).
# #         3. Throttles Tools (Social Intelligence).
# #         4. Adjusts Reasoning Framework (System 1 vs System 2).
# #         """
# #         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         mode = self.sentinel.get_mode()
        
# #         # --- 1. Cognitive Intent Routing ---
# #         # Detecting if the query is a simple greeting to save tokens/latency
# #         greetings = ["hello", "hi", "hey", "assalam", "yo", "greeting"]
# #         is_social = any(g in user_query.lower().split() for g in greetings)

# #         print(f"[AGENT] Social: {is_social} | Mode: {mode}")

# #         intent_response = "NONE"
# #         if not is_social:
# #             router_prompt = f"""
# #             You are an intent classification system.
# #             Classify the QUERY into exactly ONE category:

# #             WEB  -> Real-time info (news, weather, stocks).
# #             RAG  -> Private documents/knowledge base.
# #             DOC  -> Request to create/generate/download a file, report, or document.
# #             NONE -> General knowledge.

# #             STRICT RULES: Output ONLY one word: WEB, RAG, DOC, or NONE.

# #             QUERY: {user_query}
# #             """

# #             intent_response = self.client.chat.complete(
# #                 model="mistral-small-latest",
# #                 messages=[{"role": "user", "content": router_prompt}]
# #             ).choices[0].message.content.upper()

        
# #         print(f"[ROUTER] Intent Detected: {intent_response}")

# #         context_block = ""
        
# #         # --- 2. Strategic Tool Execution ---
# #         # Logic: Only engage tools if not a greeting and intent matches
# #         if not is_social:
# #             if "WEB" in intent_response or any(w in user_query.lower() for w in ["now", "today", "weather"]):
# #                 web_data = self.web.search(user_query)
# #                 context_block += f"\n[LATEST WEB DATA]:\n{web_data}\n"
            
# #             if "RAG" in intent_response or self.has_context:
# #                 retrieved_text = self.rag.retrieve(user_query)
# #                 context_block += f"\n[DOCUMENT CONTEXT]:\n{retrieved_text}\n"
            
# #             if "DOC" in intent_response:
# #              # We delegate immediately to the PDF handler
# #                 return self._handle_pdf_tool(user_query)

# #         # --- 3. Dynamic Strategy Selection ---
# #         # Force 'STANDARD' for social queries; otherwise use Sentinel's mode
# #         effective_mode = "STANDARD" if is_social else mode
# #         model = "mistral-large-latest" if effective_mode == "DEEP_REASONING" else "mistral-small-latest"
# #         print(f"[AGENT] Effective Mode: {effective_mode} | Model: {model}")
        
# #         # Framing the 'How' vs 'What'
# #         prompt = self._get_adaptive_prompt(effective_mode, user_query, context_block, now)
        
# #         # --- 4. Tool-Specific Fallbacks ---
# #         if "save" in user_query.lower() and "pdf" in user_query.lower():
# #             return self._handle_pdf_tool(user_query)

# #         # --- 5. Return Generator ---
# #         return self.client.chat.stream(
# #             model=model,
# #             messages=[{"role": "user", "content": prompt}]
# #         )

# #     def _get_adaptive_prompt(self, mode, query, context, time):
# #         """
# #         MASTER-LEVEL ADAPTIVE REASONING CONTROLLER
# #         Controls reasoning depth while enforcing strict grounding hierarchy.
# #         """

# #         grounding = f"""
# #     SYSTEM_METADATA:
# #     - SYSTEM_TIME: {time}

# #     GROUNDING_RULES:
# #     1. AVAILABLE_CONTEXT is the highest authority.
# #     2. If AVAILABLE_CONTEXT exists, prioritize it over prior knowledge.
# #     3. If context conflicts with prior knowledge, trust context.
# #     4. If insufficient data, explicitly state uncertainty.
# #     5. Do NOT fabricate missing details.

# #     INPUTS:
# #     - AVAILABLE_CONTEXT: {context if context else "None"}
# #     - USER_QUERY: {query}
# #     """

# #         if mode == "DEEP_REASONING":
# #             framework = """
# #     REASONING_MODE: ANALYTICAL (High Deliberation)

# #     INTERNAL_PROCESS:
# #     1. Decompose the problem.
# #     2. Extract verifiable facts from context.
# #     3. Identify assumptions (if any).
# #     4. Cross-check for logical consistency.
# #     5. Synthesize a grounded conclusion.

# #     OUTPUT_REQUIREMENTS:
# #     - Provide a structured, logically organized answer.
# #     - Do NOT expose hidden reasoning steps.
# #     - Clearly separate explanation and conclusion.
# #     """

# #         elif mode == "STANDARD":
# #             framework = """
# #     REASONING_MODE: STRUCTURED (Balanced)

# #     INTERNAL_PROCESS:
# #     - Identify key facts.
# #     - Connect them directly to the query.
# #     - Avoid unnecessary elaboration.

# #     OUTPUT_REQUIREMENTS:
# #     - Clear and concise explanation.
# #     - Direct final answer.
# #     """

# #         else:  # FAST_RESPONSE
# #             framework = """
# #     REASONING_MODE: HEURISTIC (Low Latency)

# #     INTERNAL_PROCESS:
# #     - Use strongest available signal.
# #     - Prefer brevity over depth.
# #     - Skip secondary analysis.

# #     OUTPUT_REQUIREMENTS:
# #     - Concise answer.
# #     - No extended explanation unless critical.
# #     """

# #         return f"{grounding}\n{framework}"


# #     def _handle_pdf_tool(self, query):
# #         """Yields a chunk-compatible generator for the Document Tool."""
# #         print(f"[TOOL] 📄 Generating structured document content for: {query}")
        
# #         # 1. Force the LLM to use a strict format we can parse
# #         formatting_instructions = (
# #             "You are a document generator. Output the content in strict format:\n"
# #             "- Use '# ' for Main Titles.\n"
# #             "- Use '## ' for Section Headings.\n"
# #             "- Use '* ' for bullet points.\n"
# #             "- Do NOT use bolding symbols like ** inside the text.\n"
# #             "Write a comprehensive summary about: "
# #         )
        
# #         content = self.client.chat.complete(
# #             model="mistral-large-latest",
# #             messages=[{"role": "user", "content": formatting_instructions + query}]
# #         ).choices[0].message.content
        
# #         # 2. Pass this content to the updated PDF creator
# #         path = self.docs.create_pdf(content)
        
# #         # 3. Create the response object (Standard Streamlit/Mistral chunk format)
# #         class ToolChunk:
# #             def __init__(self, text):
# #                 self.data = type('obj', (object,), {
# #                     'choices': [type('obj', (object,), {
# #                         'delta': type('obj', (object,), {'content': text})()
# #                     })()]
# #                 })()

# #         # 4. Return the special download tag
# #         yield ToolChunk(f"I have generated your document.\n\n[[DOWNLOAD:{path}]]")
from ddgs import DDGS
import datetime

class WebSearchTool:
    def __init__(self):
        # We initialize a fresh instance per search to avoid session staleness
        pass

    def search(self, query, mode="STANDARD"):
        """
        Adaptive Search:
        - FAST_RESPONSE: Shallow search (3 results), Text only.
        - STANDARD/DEEP: Deep search (8 results), Text + News fallback.
        """
        # 1. Clean the query
        clean_query = query.replace("now", "").split("2026")[0].strip()
        
        # 2. Adjust Depth based on Network Mode
        if mode == "FAST_RESPONSE":
            max_results = 3
        else:
            max_results = 8
            
        print(f"[TOOL] 🌐 Adaptive Search ({mode}): {clean_query} | Limit: {max_results}")
        
        try:
            with DDGS() as ddgs:
                # 3. Try 'Text' first
                results = list(ddgs.text(clean_query, region="wt-wt", max_results=max_results))
                
                # 4. If Text fails, immediately try 'News'
                if not results:
                    print("[TOOL] ⚠️ Text search empty. Trying Live News...")
                    results = list(ddgs.news(clean_query, region="wt-wt", max_results=max_results))

                if not results:
                    return "No live data found. Search engines returned empty results."

                # 5. Format for the LLM
                formatted_results = []
                for r in results:
                    # 'body' in text search, 'description' in news
                    content = r.get('body') or r.get('description', 'No details available.')
                    formatted_results.append(f"Title: {r['title']}\nSource: {r['href']}\nSnippet: {content}")

                return "\n\n".join(formatted_results)

        except Exception as e:
            print(f"[ERROR] Web Tool Critical Failure: {e}")
            return f"Search Error: The search provider is unreachable. (Detail: {str(e)[:50]})"

# from ddgs import DDGS  # Use the new import
# import datetime

# class WebSearchTool:
#     def __init__(self):
#         # We initialize a fresh instance per search to avoid session staleness
#         pass

#     def search(self, query, max_results=5):
#         # 1. Clean the query
#         # Remove timestamps that might confuse the search engine's indexing
#         clean_query = query.replace("now", "").split("2026")[0].strip()
        
#         print(f"[TOOL] 🌐 Multi-Stage Search: {clean_query}")
        
#         try:
#             with DDGS() as ddgs:
#                 # 2. Try 'Text' first
#                 results = list(ddgs.text(clean_query, region="wt-wt", max_results=max_results))
                
#                 # 3. If Text fails, immediately try 'News' (Higher reliability for real-time)
#                 if not results:
#                     print("[TOOL] ⚠️ Text search empty. Trying Live News...")
#                     results = list(ddgs.news(clean_query, region="wt-wt", max_results=max_results))

#                 if not results:
#                     return "No live data found. Search engines returned empty results."

#                 # 4. Format for the LLM
#                 formatted_results = []
#                 for r in results:
#                     # 'body' in text search, 'description' in news
#                     content = r.get('body') or r.get('description', 'No details available.')
#                     formatted_results.append(f"Title: {r['title']}\nSource: {r['href']}\nSnippet: {content}")

#                 return "\n\n".join(formatted_results)

#         except Exception as e:
#             print(f"[ERROR] Web Tool Critical Failure: {e}")
#             return f"Search Error: The search provider is unreachable. (Detail: {str(e)[:50]})"
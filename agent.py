import os
import ssl
from dotenv import load_dotenv

load_dotenv()

# מעקפי SSL לאינטרנט מסונן
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import httpx
original_client_init = httpx.Client.__init__
def patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = patched_client_init

from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from pinecone import Pinecone
import gradio as gr

# 1. מודל הטמעה לשאילתות
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-english-v3.0", input_type="search_query")

# 2. שימוש במודל עדכני וקיים (מונע את שגיאת ה-404)
llm = Cohere(api_key=COHERE_API_KEY, model="command-r-plus-08-2024")

# 3. חיבור לפיינקון
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)
pinecone_index = pc.Index("first")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="kiro-steering")

# 4. מנוע שליפה
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
query_engine = index.as_query_engine(llm=llm)

# 5. פונקציית מענה לגרדיו
def respond(message, history):
    try:
        response = query_engine.query(message)
        return str(response)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# 6. ממשק
demo = gr.ChatInterface(
    respond,
    title="Kiro RAG Assistant",
    description="Ask anything about the documents you uploaded to Pinecone."
)

if __name__ == "__main__":
    demo.launch(server_port=7861, share=False)
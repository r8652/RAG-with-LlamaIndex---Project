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

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.cohere import CohereEmbedding
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# 1. טעינה
reader = SimpleDirectoryReader(input_dir="kiro-steering")
documents = reader.load_data()

# 2. חיתוך
node_parser = SentenceSplitter(chunk_size=500, chunk_overlap=20)
nodes = node_parser.get_nodes_from_documents(documents=documents)

# 3. מודל הטמעה
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-english-v3.0", input_type="search_document")

# 4. חיבור לפיינקון
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)
pinecone_index = pc.Index("first")

# הגדרת ה-Vector Store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="kiro-steering")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 5. יצירה והעלאה בפועל
print("Uploading vectors directly to Pinecone...")
VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)
print("SUCCESS: Vectors successfully uploaded!")
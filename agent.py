from __future__ import annotations
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore

# --- הגדרת כלים ---
def math_calculator(expression: str) -> str:
    try: return f"Result: {eval(expression, {'__builtins__': {}}, {})}"
    except Exception as e: return f"Error: {e}"

def current_time_tool() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

math_tool = FunctionTool.from_defaults(fn=math_calculator, name="math_calculator", description="Evaluate math.")
time_tool = FunctionTool.from_defaults(fn=current_time_tool, name="current_time_tool", description="Return current time.")

class ValidationEvent(Event): query: str
class RetrievalEvent(Event): query: str; context: str

# --- ה-Workflow ---
class KiroRagWorkflow(Workflow):
    def __init__(self, retriever, llm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = retriever
        self.llm = llm
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        self.agent = ReActAgent(
            tools=[math_tool, time_tool],
            llm=self.llm,
            memory=self.memory,
            verbose=True,
            streaming=False,
        )

    @step
    async def validate_input(self, ev: StartEvent) -> ValidationEvent | StopEvent:
        query = ev.get("query", "").strip()
        if not query: return StopEvent(result="Please enter a question.")
        return ValidationEvent(query=query)

    @step
    async def retrieve_context(self, ev: ValidationEvent) -> RetrievalEvent | StopEvent:
        nodes = self.retriever.retrieve(ev.query)
        context = "\n\n".join(node.get_content() for node in nodes)
        return RetrievalEvent(query=ev.query, context=context)

    @step
    async def generate_response(self, ev: RetrievalEvent) -> StopEvent:
        # התיקון הקריטי: שימוש ב-user_msg במקום input
        response = await self.agent.run(
            user_msg=f"Context from documents:\n{ev.context}\n\nQuestion: {ev.query}"
        )
        return StopEvent(result=str(response))

# --- אתחול סביבה ---
llm = Cohere(api_key=os.getenv("COHERE_API_KEY"), model="command-r-plus-08-2024")
embed_model = CohereEmbedding(api_key=os.getenv("COHERE_API_KEY"), model_name="embed-english-v3.0")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = VectorStoreIndex.from_vector_store(
    PineconeVectorStore(pinecone_index=pc.Index("first"), namespace="kiro-steering"),
    embed_model=embed_model
)

kiro_workflow = KiroRagWorkflow(retriever=index.as_retriever(similarity_top_k=3), llm=llm)

async def chat_interface(question, history):
    result = await kiro_workflow.run(query=question)
    return str(result)

if __name__ == "__main__":
    demo = gr.ChatInterface(fn=chat_interface, title="Kiro Agentic RAG Final 🤖")
    demo.launch(share=False)

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

import gradio as gr
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore


class ValidationEvent(Event):
    query: str


class RetrievalEvent(Event):
    query: str
    context: str


def math_calculator(expression: str) -> str:
    """Evaluate a simple math expression safely."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


def format_data(data: str) -> str:
    """Format a comma-separated string into a readable list."""
    items = [item.strip() for item in data.split(",") if item.strip()]
    return " | ".join(items)


def current_time_tool() -> str:
    """Return the exact current UTC date and time."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


math_tool = FunctionTool.from_defaults(
    fn=math_calculator,
    name="math_calculator",
    description="Evaluate simple math expressions like '(3 + 5) * 2'.",
)

format_tool = FunctionTool.from_defaults(
    fn=format_data,
    name="format_data",
    description="Format comma-separated input into a clean pipe-separated list.",
)

current_time = FunctionTool.from_defaults(
    fn=current_time_tool,
    name="current_time_tool",
    description="Return the exact current UTC date and time when asked.",
)


class KiroRagWorkflow(Workflow):
    def __init__(self, retriever, llm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = retriever
        self.llm = llm
        self.memory = ChatMemoryBuffer(token_limit=3000)

    @step
    async def validate_input(self, ev: StartEvent) -> ValidationEvent | StopEvent:
        user_query = ev.get("query", "").strip()
        if not user_query:
            return StopEvent(result="Please enter a valid question.")
        return ValidationEvent(query=user_query)

    @step
    async def retrieve_context(self, ev: ValidationEvent) -> RetrievalEvent | StopEvent:
        retrieved_nodes = self.retriever.retrieve(ev.query)
        if not retrieved_nodes:
            return StopEvent(
                result=(
                    "I couldn't find relevant information in the uploaded documents "
                    "to answer that question."
                )
            )
        context_str = "\n\n".join(node.get_content() for node in retrieved_nodes)
        return RetrievalEvent(query=ev.query, context=context_str)

    @step
    async def generate_response(self, ev: RetrievalEvent) -> StopEvent:
        chat_history = self.memory.get_all()
        history_text = (
            "\n".join(f"{msg.role}: {msg.content}" for msg in chat_history)
            if chat_history
            else ""
        )

        response = self.llm.predict_and_call(
            tools=[math_tool, format_tool, current_time],
            user_msg=(
                f"Conversation history:\n{history_text}\n\n"
                f"Retrieved context:\n{ev.context}\n\n"
                f"Question: {ev.query}"
            ),
            chat_history=chat_history,
            verbose=False,
            allow_parallel_tool_calls=False,
            error_on_no_tool_call=False,
        )
        answer = str(response.response)

        self.memory.put(ChatMessage(role="user", content=ev.query))
        self.memory.put(ChatMessage(role="assistant", content=answer))

        return StopEvent(result=answer)


COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not COHERE_API_KEY or not PINECONE_API_KEY:
    raise RuntimeError(
        "Please set COHERE_API_KEY and PINECONE_API_KEY in your .env file."
    )

embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_query",
)

llm = Cohere(api_key=COHERE_API_KEY, model="command-r-plus-08-2024")

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("first")
vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    namespace="kiro-steering",
)
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
retriever = index.as_retriever(similarity_top_k=3)

kiro_workflow = KiroRagWorkflow(retriever=retriever, llm=llm, timeout=30)


def _normalize_history(history):
    """Convert Gradio history entries into ChatMessage objects."""
    if not history:
        return []

    normalized = []
    for item in history:
        if isinstance(item, Mapping):
            role = item.get("role") or item.get("from")
            content = item.get("content")
            if role and content is not None:
                normalized.append(ChatMessage(role=str(role), content=str(content)))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            role, content = item[0], item[1]
            if isinstance(role, str) and content is not None:
                normalized.append(ChatMessage(role=role, content=str(content)))
    return normalized


async def chat_interface(question: str, history):
    try:
        for msg in _normalize_history(history):
            kiro_workflow.memory.put(msg)

        result = await kiro_workflow.run(query=question)
        return str(result)
    except Exception as e:
        print(f"[Error] {e}")
        return f"An internal error occurred: {e}"


demo = gr.ChatInterface(
    fn=chat_interface,
    title="Kiro Agentic RAG",
    description="Ask questions about your uploaded project documents.",
)


if __name__ == "__main__":
    demo.launch(server_port=7861)

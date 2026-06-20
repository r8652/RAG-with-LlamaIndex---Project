Kiro Agentic RAG Project 🤖
פרויקט מבוסס AI המשלב RAG (Retrieval-Augmented Generation) יחד עם Agentic Workflow כדי לספק תשובות מדויקות, מבוססות ידע ארגוני, עם יכולת הפעלת כלים בזמן אמת.

🚀 אודות הפרויקט
פרויקט Kiro נועד לסייע למשתמשים לקבל מידע על הפרויקט מתוך מסמכים טכניים, תוך שילוב כלים חיצוניים לחישובים מתמטיים ודיווח זמן מדויק. הפרויקט משתמש בטכנולוגיית ה-Workflow העדכנית ביותר של LlamaIndex.

🛠 טכנולוגיות מרכזיות
Framework: LlamaIndex (Workflows & ReAct Agents).

LLM & Embeddings: Cohere (Command R+ & Embed v3).

Vector Database: Pinecone.

Interface: Gradio.

✨ מאפיינים עיקריים
Agentic RAG: שליפה חכמה של מידע מהמסמכים ב-Pinecone.

Tool Use: יכולת אוטונומית להפעיל כלים (מחשבון ושעון UTC).

Memory Management: ניהול זיכרון שיחה מובנה באמצעות ChatMemoryBuffer.

Clean Workflow: ארכיטקטורה מודולרית המפרידה בין אימות קלט, שליפה, וסינתזה.
ENV
COHERE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
התקנות
pip install llama-index llama-index-llms-cohere llama-index-embeddings-cohere llama-index-vector-stores-pinecone gradio pinecone-client python-dotenv
הרצת הפרויקט
python agent.py
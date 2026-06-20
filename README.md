Kiro Agentic RAG 🤖
פרויקט זה הוא מערכת Agentic RAG (Retrieval-Augmented Generation) מתקדמת, המבוססת על LlamaIndex ו-Workflows. המערכת מאפשרת למשתמש לשאול שאלות על מסמכי הפרויקט ולקבל תשובות חכמות המבוססות על שליפה ממאגר וקטורי, תוך שילוב כלים חיצוניים וזיכרון שיחה.

🛠 טכנולוגיות
Framework: LlamaIndex (Workflows, Agents, Memory)

LLM: Cohere (Command R+)

Vector Database: Pinecone

UI: Gradio

Language: Python

🚀 תכונות המערכת
RAG (Retrieval-Augmented Generation): שליפת מידע רלוונטי ממסמכי הפרויקט המאוחסנים ב-Pinecone.

Agentic Capabilities: שימוש ב-FunctionTool המאפשר למערכת לבצע פעולות (כמו קבלת זמן נוכחי) באופן עצמאי.

Event-Driven Workflow: שימוש ב-Workflow של LlamaIndex לניהול זרימת השלבים (Validation -> Retrieval -> Generation).

Conversation Memory: שימוש ב-ChatMemoryBuffer לשמירת הקשר השיחה.
אופן פעולת ה-Agentic Workflow:
המערכת שלי משתמשת ב-Workflow של LlamaIndex כדי להפריד בין תחומי אחריות:

עיבוד קלט (Input Validation): סינון ומניעת קלט ריק.

Retrieval (RAG): שליפה סמנטית של מידע רלוונטי מתוך בסיס הנתונים הוקטורי (Pinecone).

Reasoning (Agentic): המערכת מחליטה האם להשתמש במידע שהתקבל מה-RAG או להפעיל FunctionTool (כמו כלי הזמן) בהתאם לצורך.

זיכרון (Memory): ניהול היסטוריית שיחה באמצעות ChatMemoryBuffer, המאפשר למודל להבין את ההקשר של שאלות המשך (Follow-up questions).
# Kiro RAG Assistant 🤖

פרויקט זה מציג מערכת RAG (Retrieval-Augmented Generation) מתקדמת המבוססת על LlamaIndex, Pinecone ו-Cohere. המערכת מאפשרת למשתמשים לנהל צ'אט אינטראקטיבי מבוסס בינה מלאכותית עם מסמכי הניהול ועקרונות ההיגוי של פרויקט Kiro.

## 🚀 ארכיטקטורת המערכת (Workflow)
המערכת פועלת בשני שלבים עיקריים:
1. **שלב ההכנה (prepare.py):** טעינת מסמכי המקור מתיקיית `kiro-steering`, פירוקם לחלקים (Nodes), יצירת Embeddings בעזרת מודל `embed-english-v3.0` של Cohere, ושמירתם בבסיס הנתונים הוקטורי Pinecone תחת ה-Namespace `kiro-steering`.
2. **שלב הסוכן (agent.py):** יצירת ממשק צ'אטבוט אינטראקטיבי בעזרת Gradio, שולף מידע רלוונטי מ-Pinecone ומנסח תשובות מדויקות בעזרת מודל ה-LLM `command-r-plus-08-2024` של Cohere.

## 🛠️ איך להריץ את הפרויקט

### 1. התקנת ספריות נדרשות:
יש לוודא שכל הספריות מותקנות במחשב על ידי הרצת הפקודה בטרמינל:
```bash
pip install llama-index llama-index-vector-stores-pinecone llama-index-embeddings-cohere llama-index-llms-cohere pinecone python-dotenv gradio httpx urllib3
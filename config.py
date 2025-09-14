import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model_name = "llama-3.3-70b-versatile"

llm_model = ChatGroq(
    model=model_name,
    api_key=os.getenv("GROQ_API_KEY"),
)

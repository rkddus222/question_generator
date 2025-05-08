from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

gpt_fouro_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0, top_p=1)
llm = ChatOpenAI(model="gpt-4o", temperature=0, top_p=1)
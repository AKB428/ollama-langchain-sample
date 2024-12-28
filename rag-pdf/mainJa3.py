from langchain.document_loaders import OnlinePDFLoader
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
import sys
import os
from transformers import AutoTokenizer, AutoModel
import torch
from langchain.embeddings.base import Embeddings

# コマンドライン引数からPDFのURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_URL>")
    sys.exit(1)

pdf_url = sys.argv[1]
loader = OnlinePDFLoader(pdf_url)
data = loader.load()

# https://touch-sp.hatenablog.com/entry/2024/07/31/081420
# ベクトルストア作成
embed_model_id = "pkshatech/GLuCoSE-base-ja"
embeddings = HuggingFaceEmbeddings(model_name=embed_model_id)

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")
llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

index = VectorstoreIndexCreator(
    vectorstore_cls=Chroma,
    embedding=embeddings
).from_loaders([loader])    

while True:
    query = input("\n質問: ")
    if query == "exit":
        break
    answer = index.query(query, llm=llm)
    print(answer)
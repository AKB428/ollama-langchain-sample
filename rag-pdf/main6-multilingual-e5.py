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
import unicodedata

# コマンドライン引数からPDFのURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_URL>")
    sys.exit(1)

pdf_url = sys.argv[1]
loader = OnlinePDFLoader(pdf_url)
data = loader.load()

# https://highreso.jp/edgehub/machinelearning/langchainpdf.html
# ベクトルストア作成
embed_model_id = "intfloat/multilingual-e5-large"
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
    
    # 入力を正規化して制御文字や不正な空白を削除
    query = unicodedata.normalize("NFKC", query).strip()

    # 空のクエリや不正なクエリをスキップ
    if not query:
        print("空のクエリです。再入力してください。")
        continue
    
    if query == "exit":
        break
    answer = index.query(query, llm=llm)
    print(answer)
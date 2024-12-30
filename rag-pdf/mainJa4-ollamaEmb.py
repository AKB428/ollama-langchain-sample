from langchain_community.document_loaders import OnlinePDFLoader
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import OllamaEmbeddings
import sys
import os
from langchain_ollama import OllamaEmbeddings

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")

# コマンドライン引数からPDFのURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_URL>")
    sys.exit(1)

pdf_url = sys.argv[1]
loader = OnlinePDFLoader(pdf_url)
data = loader.load()

# https://touch-sp.hatenablog.com/entry/2024/07/31/081420
# https://note.com/catap_art3d/n/n1ae2474509b7
# ベクトルストア作成
embed_model_id = "kun432/cl-nagoya-ruri-large"
embeddings = OllamaEmbeddings(model=embed_model_id, base_url=f"http://{ollama_host}:11434")

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
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
import sys
import os
import unicodedata

# コマンドライン引数からPDFのURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_URL>")
    sys.exit(1)

pdf_url = sys.argv[1]
loader = PyPDFLoader(pdf_url)

# https://highreso.jp/edgehub/machinelearning/langchainpdf.html
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
    query = input("\query: ")

    if query == "exit":
        break
    answer = index.query(query, llm=llm)
    print(answer)
from langchain.document_loaders import OnlinePDFLoader
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_huggingface import HuggingFaceEmbeddings
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

# テキスト分割
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)


# https://touch-sp.hatenablog.com/entry/2024/07/31/081420
# ベクトルストア作成
embed_model_id = "pkshatech/GLuCoSE-base-ja"
embeddings = HuggingFaceEmbeddings(model_name=embed_model_id)
vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)

# RAGセットアップ
template = """以下の文脈を使用して、最後にある質問に答えてください。
答えがわからない場合は、わからないと言ってください。答えを作り出そうとしないでください。
回答は最大3文で簡潔にまとめてください。
{context}
質問: {question}
役立つ答え:"""
QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)

while True:
    query = input("\n質問: ")
    if query == "exit":
        break

    # 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
    ollama_host = os.getenv("OLLAMA_HOST", "localhost")
    llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,  # 適切なLLMを選択
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )
    result = qa_chain({"query": query})
    print("\n回答:", result['result'])

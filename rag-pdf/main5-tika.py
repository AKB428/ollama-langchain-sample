from tika import parser  # tikaライブラリでPDFを解析
from langchain.document_loaders import TextLoader
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
import tempfile  # 一時ファイル作成用

# コマンドライン引数からPDFのローカルパスを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_PATH>")
    sys.exit(1)

pdf_path = sys.argv[1]

# Tikaを使用してPDFをテキスト化
print("Extracting text from PDF...")
parsed_pdf = parser.from_file(pdf_path)
pdf_text = parsed_pdf.get("content", "").strip()

if not pdf_text:
    print("Failed to extract text from the PDF. Please check the file.")
    sys.exit(1)

# PDFテキストを一時ファイルに保存
with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as temp_file:
    temp_file.write(pdf_text)
    temp_file_path = temp_file.name

# TextLoaderで一時ファイルを読み込む
loader = TextLoader(temp_file_path)

# ベクトルストア作成
embed_model_id = "pkshatech/GLuCoSE-base-ja"
embeddings = HuggingFaceEmbeddings(model_name=embed_model_id)

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")
llm = OllamaLLM(
    model="llama3.2",
    base_url=f"http://{ollama_host}:11434",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

index = VectorstoreIndexCreator(
    vectorstore_cls=Chroma,
    embedding=embeddings
).from_loaders([loader])

# 質問応答ループ
while True:
    query = input("\n質問: ")
    if query.lower() == "exit":
        break
    answer = index.query(query, llm=llm)
    print("\n回答:", answer)

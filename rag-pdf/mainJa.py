from langchain.document_loaders import OnlinePDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import GPT4AllEmbeddings
from langchain import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
import sys
import os

class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

# コマンドライン引数からPDFのURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <PDF_URL>")
    sys.exit(1)

pdf_url = sys.argv[1]

# PDFをロードし、チャンクに分割
loader = OnlinePDFLoader(pdf_url)
data = loader.load()

from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

with SuppressStdout():
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=GPT4AllEmbeddings())

while True:
    query = input("\n質問: ")
    query = query.encode('utf-8', 'surrogatepass').decode('utf-8')

    if query == "exit":
        break
    if query.strip() == "":
        continue

    # プロンプト（日本語版）
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

    # 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
    ollama_host = os.getenv("OLLAMA_HOST", "localhost")
    llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )

    result = qa_chain({"query": query})
    print("\n回答:", result['result'])

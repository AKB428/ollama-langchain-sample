from langchain.document_loaders import OnlinePDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import sys
import os
from transformers import AutoTokenizer, AutoModel
import torch
from langchain.embeddings.base import Embeddings

# 日本語埋め込み用クラス
class RuriEmbeddings:
    def __init__(self, model_name="cl-nagoya/ruri-large"):
        # モデルとトークナイザーのロード
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_text(self, text):
        # テキストをトークナイズ
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        # モデルで埋め込み生成
        with torch.no_grad():
            outputs = self.model(**inputs)
            # [CLS]トークンの埋め込みを取得
            embeddings = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        return embeddings

    def embed_documents(self, texts):
        # 複数テキストを一括で埋め込み
        return [self.embed_text(text) for text in texts]

class HuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name="cl-nagoya/ruri-large"):
        self.embedder = RuriEmbeddings(model_name=model_name)

    def embed_documents(self, texts):
        return self.embedder.embed_documents(texts)

    def embed_query(self, text):
        return self.embedder.embed_text(text)

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

# ベクトルストア作成
embedding_function = HuggingFaceEmbeddings(model_name="cl-nagoya/ruri-large")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=embedding_function)

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

    qa_chain = RetrievalQA.from_chain_type(
        llm=None,  # 適切なLLMを選択
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )
    result = qa_chain({"query": query})
    print("\n回答:", result['result'])

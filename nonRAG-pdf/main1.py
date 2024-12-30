import os
import sys
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import OnlinePDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

# コマンドライン引数からURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <URL or filePath>")
    sys.exit(1)
url = sys.argv[1]

loader = OnlinePDFLoader(url)
docs = loader.load()

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")

# プロンプトテンプレートの設定
PROMPT = PromptTemplate(
    input_variables=["text"],
    template="以下の内容を日本語で要約してください、:\n\n{text}\n\n要約:"
)

# LLMモデルの設定
llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434")
chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)

# 要約の実行
result = chain.invoke(docs)
#print(result)
print(result['output_text'])

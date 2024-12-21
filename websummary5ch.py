import os
import sys
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# コマンドライン引数からURLを取得
if len(sys.argv) < 2:
    print("Usage: python script.py <URL>")
    sys.exit(1)
url = sys.argv[1]

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")

# プロンプトテンプレートの設定（要約用）
SUMMARY_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="以下のWEBページの本文部分を日本語で要約してください:\n\n{text}\n\n要約:"
)

# プロンプトテンプレートの設定（5ch風会話劇用）
DISCUSSION_PROMPT = PromptTemplate(
    input_variables=["summary"],
    template=(
        "以下はWEBサイトの記事を要約したものです:\n\n{summary}\n\n"
        "この記事をもとに、日本のネット掲示板「5ch」風の会話劇を作成してください。\n"
        "登場人物は「名無しさん」「知識人」「初心者」など自由に追加してよいです。\n"
        "自然な流れになるようにしてください。"
    )
)

# Webページの内容をロード
loader = WebBaseLoader(url)
docs = loader.load()

# LLMモデルの設定
llm = OllamaLLM(model="llama3.3", base_url=f"http://{ollama_host}:11434")

# 要約チェーンの実行
summary_chain = load_summarize_chain(llm, chain_type="stuff", prompt=SUMMARY_PROMPT)
summary_result = summary_chain.invoke(docs)
summary_text = summary_result['output_text']

# 会話劇生成のチェーン
discussion_chain = LLMChain(llm=llm, prompt=DISCUSSION_PROMPT)
discussion_result = discussion_chain.run({"summary": summary_text})

# 結果の出力
print("要約:")
print(summary_text)
print("\n5ch風会話劇:")
print(discussion_result)

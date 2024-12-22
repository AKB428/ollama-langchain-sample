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
PROMPT = PromptTemplate(
    input_variables=["text"],
    template="以下のWEBページの本文部分を要約してください:\n\n{text}\n\n要約:"
)

# Webページの内容をロード
loader = WebBaseLoader(url)
docs = loader.load()

# LLMモデルの設定
llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434")
chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)

# 要約の実行
result = chain.invoke(docs)
summary_text = result['output_text']

# 翻訳プロンプトの設定
TRANSLATION_PROMPT = PromptTemplate(
    input_variables=["summary"],
    template="以下の要約文を正確に日本語に翻訳してください:\n\n{summary}\n\n翻訳:"
)

# 翻訳チェーンの設定
translation_chain = LLMChain(llm=llm, prompt=TRANSLATION_PROMPT)
translation_result = translation_chain.run({"summary": summary_text})

# 結果の出力
print("生成された要約:")
print(summary_text)
print("\n翻訳された要約:")
print(translation_result)

# 5ch風会話劇のプロンプト設定
DISCUSSION_PROMPT = PromptTemplate(
    input_variables=["translated_summary"],
    template=(
        "以下は翻訳された要約文です:\n\n{translated_summary}\n\n"
        "この内容をもとに、日本のネット掲示板「5ch」風の会話スレッド風会話劇を作成してください。\n"
        "登場人物は「名無しさん」「知識人」「初心者」など自由に追加してよいです。\n"
        "自然な流れになるようにしてください。"
    )
)

# 5ch風会話劇のチェーン設定
discussion_chain = LLMChain(llm=llm, prompt=DISCUSSION_PROMPT)
discussion_result = discussion_chain.run({"translated_summary": translation_result})

# 結果の出力
print("\n5ch風会話劇:")
print(discussion_result)

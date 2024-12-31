from tika import parser  # tikaライブラリでPDFを解析
from langchain.document_loaders import TextLoader
from langchain_ollama import OllamaLLM
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import sys
import os
import tempfile  # 一時ファイル作成用
from langchain.chains import LLMChain

# 環境変数からOLLAMA_HOSTを取得（未設定の場合はlocalhostを使用）
ollama_host = os.getenv("OLLAMA_HOST", "localhost")

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
# プロンプトテンプレートの設定（要約用）
SUMMARY_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="以下のPDFから抽出したテキストを要約してください:\n\n{text}\n\n要約:"
)

# プロンプトテンプレートの設定（5ch風会話劇用）
DISCUSSION_PROMPT = PromptTemplate(
    input_variables=["summary"],
    template=(
        "以下はPDFから抽出したテキストを要約したものです:\n\n{summary}\n\n"
        "この記事をもとに、日本のネット掲示板「5ch」風の会話劇を作成してください。"
    )
)

docs = loader.load()

# LLMモデルの設定
llm = OllamaLLM(model="llama3.2", base_url=f"http://{ollama_host}:11434")

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
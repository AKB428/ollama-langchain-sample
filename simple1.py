from langchain.llms import Ollama

input = input("What is your question?\n> ")
llm = Ollama(model="llama3.2", base_url="http://192.168.1.9:11434" )
res = llm.invoke(input)
print (res)

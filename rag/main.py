from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = './韩飞龙-6月工作总结.pdf'
loader   = PyPDFLoader(file_path)

docs = loader.load()
print(docs[0].page_content)
print(docs[0].metadata)
print(len(docs))

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
print(len(all_splits))
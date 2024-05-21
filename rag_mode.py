from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

global chain

### PDF INPUT STAGE ###
def rag(local_path):
    if local_path:
        loader = UnstructuredPDFLoader(file_path=local_path)
        data = loader.load()
    else:
        # print("Upload a PDF file")
        return "Error. Upload a PDF file"


    ### SPLITTING, CHUNKING AND VECTOR EMBEDDINGS STAGE ###
    # Splitting and chunking
    text_splitter = RecursiveCharacterTextSplitter()
    chunks = text_splitter.split_documents(data)

    # Adding to vector database
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=OllamaEmbeddings(model="nomic-embed-text",show_progress=True),
        collection_name="local-rag"
    )

    ### RETRIEVAL AND OUTPUT STAGE ###
    # Choosing LLM from Ollama
    local_model = "llama3"
    llm = ChatOllama(model=local_model)

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), 
        llm,
        prompt=QUERY_PROMPT
    )

    # RAG prompt
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    global chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def rag_response(user_query):
    global chain
    llm_response = chain.invoke(user_query)
    return llm_response

if __name__ == "__main__":
    rag("summarize this document", "/Users/manasgandhi/Downloads/wework_financial_document.pdf")
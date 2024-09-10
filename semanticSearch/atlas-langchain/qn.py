import argparse
import params
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")

parser = argparse.ArgumentParser(description='Atlas Vector Search Demo')
parser.add_argument('-q', '--question', help="The question to ask")
args = parser.parse_args()

if args.question is None:
    query = "How big is the telecom company?"
    query = "Who started AT&T?"
    query = "Where is AT&T based?"
    query = "What venues are AT&T branded?"
    query = "How big is BofA?"
    query = "When was the financial institution started?"
    query = "Does the bank have an investment arm?"
    query = "Where does the bank's revenue come from?"
    query = "Tell me about charity."
    query = "What buildings are BofA branded?"

else:
    query = args.question

print("\nYour question:")
print("-------------")
print(query)

def get_answer(question):
    client = MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True)
    collection = client[params.db_name][params.collection_name]

    # initialize vector store
    vectorStore = MongoDBAtlasVectorSearch(
        collection, OpenAIEmbeddings(openai_api_key=params.openai_api_key), index_name=params.index_name
    )
    docs = vectorStore.max_marginal_relevance_search(question, K=1)
    
    llm = OpenAI(openai_api_key=params.openai_api_key, temperature=0)
    compressor = LLMChainExtractor.from_llm(llm)

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=vectorStore.as_retriever()
    )

    compressed_docs = compression_retriever.invoke(question)
    response = {
        "title": compressed_docs[0].metadata['title'],
        "content": compressed_docs[0].page_content
    }
    
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Atlas Vector Search Demo')
    parser.add_argument('-q', '--question', help="The question to ask")
    args = parser.parse_args()

    if args.question is not None:
        query = args.question
        response = get_answer(query)
        print("\nYour question:")
        print("-------------")
        print(query)
        print("\nAI Response:")
        print("-----------")
        print(response["title"])
        print(response["content"])





# import argparse
# import re 
# import params 
# from pymongo import MongoClient
# from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings
# import warnings


# warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")

# def get_answer(question):
#     client = MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True)
#     collection = client[params.db_name][params.collection_name]

#     # Generate the query embedding
#     embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)
#     query_embedding = embeddings.embed_query(question)

#     print("Query Embedding:", query_embedding)

#     vectorStore = MongoDBAtlasVectorSearch(
#         collection, embeddings, index_name=params.index_name
#     )

#     # Perform the search and capture the results
#     docs = vectorStore.max_marginal_relevance_search(question, K=5)

#     print(f"Number of documents found: {len(docs)}")
#     for doc in docs:
#         doc_id = doc.get('_id', 'Unknown ID')
#         doc_title = doc.get('title', 'No title available')
#         doc_text = doc.get('text', 'No content available')

#         print(f"Doc ID: {doc_id}, Title: {doc_title}")
#         print(f"Text snippet: {doc_text[:150]}...")

#     if docs:
#         doc = docs[0]
#         content = doc.page_content

#         # Extract the title and content
#         title = doc.metadata.get('title', 'No title available') if hasattr(doc, 'metadata') else 'No metadata available'

#         print(f"Top document title: {title}")
#         print(f"Content snippet: {content[:150]}...")

#         return {
#             "title": title,
#             "content": content
#         }
#     else:
#         print("No relevant documents found for the query.")
#         return {"error": "No relevant documents found for the query."}

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Atlas Vector Search Demo')
#     parser.add_argument('-q', '--question', help="The question to ask", required=True)
#     args = parser.parse_args()

#     response = get_answer(args.question)

#     print("\nResponse:")
#     print("---------")
#     for res in response:
#         if isinstance(res, dict) and "error" not in res:
#             print(f"Title: {res['title']}")
#             print(f"Content: {res['content'][:150]}...") 
#             print(f"Extracted Text: {res['extracted_text']}\n")
#         else:
#             print(res)

# import argparse
# import re
# import params
# from pymongo import MongoClient
# from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings
# import warnings


# warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")

# def get_answer(question):
#     try:
#         client = MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True)
#         collection = client[params.db_name][params.collection_name]

#         embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)
#         query_embedding = embeddings.embed_query(question)
#         # print('Query embedding:', query_embedding)

#         vectorStore = MongoDBAtlasVectorSearch(
#             collection, embeddings, index_name=params.index_name
#         )

#         docs = vectorStore.max_marginal_relevance_search(question, K=11)
#         print(f"Number of documents found: {len(docs)}")

#         if len(docs) == 0:
#             return {"error": "No documents found."}

#         question_keywords = question.lower().split()

#         filtered_docs = [doc for doc in docs if any(keyword in doc.metadata.get('title', '').lower() for keyword in question_keywords)]

#         if not filtered_docs:
#             print("No documents with matching titles found.")
#             # return {"error": "No documents with matching titles found."}

#         for doc in filtered_docs:
#             # print(doc)

#             doc_title = doc.metadata['title'] if 'title' in doc.metadata else 'No title available'
#             doc_content = doc.page_content if doc.page_content else 'No content available'

#             print(f"Title: {doc_title}")
#             print(f"Content snippet: {doc_content[:150]}...")

#             # Search for the pattern in the content
#             # pattern = r"RP/0/0/CPU0:router.*"
#             # matches = re.findall(pattern, doc_content, re.MULTILINE)
#         pattern = r"RP/0/0/CPU0:router.*?(?=\nRP/0/0/CPU0:router|$)"
#         matches = re.findall(pattern, doc_content, re.MULTILINE | re.DOTALL)
#         for match in matches:
#             lines = match.strip().split('\n')
#             for line in lines:
#                 print(line)
#             print(f"Match found in document titled '{doc_title}':\n{match}")
#         for fil  in filtered_docs:
#             print('these are filtered docs', fil)
#         if filtered_docs:
#             doc = filtered_docs[0]
#             content = doc.page_content if doc.page_content else 'No content available'
#             title = doc.metadata['title'] if 'title' in doc.metadata else 'No title available'

#             print(f"Top document title: {title}")
#             print(f"Content snippet: {content[:150]}...")

#             return {
#                 "title": title,
#                 "content": content
#             }

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return {"error": str(e)}


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Atlas Vector Search Demo')
#     parser.add_argument('-q', '--question', help="The question to ask", required=True)
#     args = parser.parse_args()

#     response = get_answer(args.question)

#     print("\nResponse:")
#     print("---------")
#     if response is not None:
#         if "error" not in response:
#             print(f"Title: {response['title']}")
#             print(f"Content: {response['content']}")
#         else:
#             print(response['error'])
#     else:
#         print("No response was returned from the get_answer function.")


# def get_answer(question):
#     client = MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True)
#     collection = client[params.db_name][params.collection_name]

#     # Generate the query embedding
#     embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)
#     query_embedding = embeddings.embed_query(question)

#     print("Query Embedding:", query_embedding)

#     vectorStore = MongoDBAtlasVectorSearch(
#         collection, embeddings, index_name=params.index_name
#     )

#     docs = vectorStore.max_marginal_relevance_search(question, K=5)

#     print(f"Number of documents found: {len(docs)}")

#     for doc in docs:
#         if hasattr(doc, '_id') and isinstance(doc._id, dict) and '$oid' in doc._id:
#             doc_id = doc._id['$oid']
#         else:
#             doc_id = 'Unknown ID'

#         doc_title = getattr(doc, 'title', 'No title available')
#         doc_text = getattr(doc, 'text', 'No content available')

#         print(f"Doc ID: {doc_id}, Title: {doc_title}")
#         print(f"Text snippet: {doc_text[:150]}...")

#     if docs:
#         print('All docs:',docs[0])

#     if docs:
#         doc = docs[0]
#         if isinstance(doc, dict):
#             content = doc.get('page_content', 'No content available')
#             title = doc.get('metadata', {}).get('title', 'No title available')
#         else:
#             content = getattr(doc, 'page_content', 'No content available')
#             metadata = getattr(doc, 'metadata', {})
#             title = metadata.get('title', 'No title available') if isinstance(metadata, dict) else 'No title available'

#         print(f"Top document title: {title}")
#         print(f"Content snippet: {content[:150]}...")

#         return {
#             "title": title,
#             "content": content
#         }

#     else:
#         print("No relevant documents found for the query.")
#         return {"error": "No relevant documents found for the query."}


# for doc in docs:
#         # Extract the document ID, handling the case where it's nested under the '$oid' key
#     doc_id = doc.get('_id', {}).get('$oid', 'Unknown ID')
#         # Extract the title
#     doc_title = doc.get('title', 'No title available')
#         # Extract the text content
#     doc_text = doc.get('text', 'No content available')

#     # Debugging: Print the document details
#     print(f"Doc ID: {doc_id}, Title: {doc_title}")
#     print(f"Text snippet: {doc_text[:150]}...")

from flask import Flask, jsonify, request, render_template
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from PyPDF2 import PdfReader
from io import BytesIO
from query import get_answer
import params
import requests



app = Flask(__name__)

# requests.get('https://google.com', verify=False)
def load_pdf_from_url():
    reader = PdfReader("chapter9.pdf")
    page = reader.pages[0]
    print(page.extract_text())

def process_documents():
        # Step 1: Load

        print("Loading")
        pdf_url = "https://www.cisco.com/c/en/us/td/docs/routers/xr12000/software/xr12k_r4-0/system_management/command/reference/yr40xr12k_chapter9.pdf"   

        # Load PDF and extract text
        data = load_pdf_from_url(pdf_url)
        
        # print("Loading")
        # loaders =[ 
        # WebBaseLoader("https://www.cisco.com/c/en/us/td/docs/routers/xr12000/software/xr12k_r4-0/system_management/command/reference/yr40xr12k_chapter9.html", requests_kwargs={'verify': False})
        # WebBaseLoader("https://en.wikipedia.org/wiki/AT%26T"),
        # WebBaseLoader("https://en.wikipedia.org/wiki/Bank_of_America")
        # WebBaseLoader("https://en.wikipedia.org/wiki/Regular_moon")
        # ]
        # loaders.requests_kwargs = {'verify':False}
        
        # data = []
        # for loader in loaders:
        #     data.extend(loader.load())
        print(data)
        # Step 2: Transform (Split)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n\n", "\n", "(?<=\\. )", " "], length_function=len)
        docs = text_splitter.split_documents(data)
        print('Split into ' + str(len(docs)) + ' docs')
        # Step 3: Embed
        # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
        embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)

        # Step 4: Store
        # # Initialize MongoDB python client
        # try:
        #     client = MongoClient(params.mongodb_conn_string)

        with MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True) as client:
            collection = client[params.db_name][params.collection_name]

            # Check if the collection is empty
            if collection.count_documents({}) == 0:
                print("Adding data...")

                # Reset without deleting the Search Index
                collection.delete_many({})

                # Insert the documents in MongoDB Atlas with their embedding
                MongoDBAtlasVectorSearch.from_documents(
                    docs, embeddings, collection=collection, index_name=params.index_name
                )
                print("Documents loaded and stored successfully.")
            else:
                print("The collection already has documents.")

            #     docsearch = MongoDBAtlasVectorSearch.from_documents(
            #         docs, embeddings, collection=collection, index_name=params.index_name
            #     )
            # return jsonify({"message": "Documents loaded and stored successfully", "num_docs": len(docs)})

@app.route('/', methods=['GET'])
def index():
    return render_template('quest.html') 
   
@app.route('/ask', methods=['GET'])
def ask_question():
    question = request.args.get('question')
    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    try:
        answer = get_answer(question) 
        print(answer)
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_pdf_from_url()  
    app.run(debug=True, use_reloader=False)







#     from flask import Flask, jsonify, request, render_template
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.document_loaders import WebBaseLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_mongodb import MongoDBAtlasVectorSearch
# from pymongo import MongoClient
# from PyPDF2 import PdfReader
# from io import BytesIO
# from query import get_answer
# import params
# import requests



# app = Flask(__name__)

# # requests.get('https://google.com', verify=False)
# def load_pdf_from_url():
#     reader = PdfReader("chapter9.pdf")
#     page = reader.pages[0]
#     print(page.extract_text())

# def process_documents():
#         # Step 1: Load

#         print("Loading")
#         # pdf_url = "https://www.cisco.com/c/en/us/td/docs/routers/xr12000/software/xr12k_r4-0/system_management/command/reference/yr40xr12k_chapter9.pdf"   

#         # Load PDF and extract text
#         # data = load_pdf_from_url(pdf_url)
        
#         # print("Loading")
#         # loaders =[ 
#         # WebBaseLoader("https://www.cisco.com/c/en/us/td/docs/routers/xr12000/software/xr12k_r4-0/system_management/command/reference/yr40xr12k_chapter9.html", requests_kwargs={'verify': False})
#         # WebBaseLoader("https://en.wikipedia.org/wiki/AT%26T"),
#         # WebBaseLoader("https://en.wikipedia.org/wiki/Bank_of_America")
#         # WebBaseLoader("https://en.wikipedia.org/wiki/Regular_moon")
#         # ]
#         # loaders.requests_kwargs = {'verify':False}
        
#         # data = []
#         # for loader in loaders:
#         #     data.extend(loader.load())
#         # print(data)
#         # Step 2: Transform (Split)
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n\n", "\n", "(?<=\\. )", " "], length_function=len)
#         docs = text_splitter.split_documents(data)
#         print('Split into ' + str(len(docs)) + ' docs')
#         # Step 3: Embed
#         # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
#         embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)

#         # Step 4: Store
#         # # Initialize MongoDB python client
#         # try:
#         #     client = MongoClient(params.mongodb_conn_string)

#         with MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True) as client:
#             collection = client[params.db_name][params.collection_name]

#             # Check if the collection is empty
#             if collection.count_documents({}) == 0:
#                 print("Adding data...")

#                 # Reset without deleting the Search Index
#                 collection.delete_many({})

#                 # Insert the documents in MongoDB Atlas with their embedding
#                 MongoDBAtlasVectorSearch.from_documents(
#                     docs, embeddings, collection=collection, index_name=params.index_name
#                 )
#                 print("Documents loaded and stored successfully.")
#             else:
#                 print("The collection already has documents.")

#             #     docsearch = MongoDBAtlasVectorSearch.from_documents(
#             #         docs, embeddings, collection=collection, index_name=params.index_name
#             #     )
#             # return jsonify({"message": "Documents loaded and stored successfully", "num_docs": len(docs)})

# @app.route('/', methods=['GET'])
# def index():
#     return render_template('quest.html') 
   
# @app.route('/ask', methods=['GET'])
# def ask_question():
#     question = request.args.get('question')
#     if not question:
#         return jsonify({"error": "Please provide a question."}), 400

#     try:
#         answer = get_answer(question) 
#         print(answer)
#         return jsonify({"question": question, "answer": answer})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     load_pdf_from_url()  
#     app.run(debug=True, use_reloader=False)
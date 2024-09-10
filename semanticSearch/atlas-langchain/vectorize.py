from flask import Flask, jsonify, request, render_template
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import params
import re
import fitz
from query import get_answer

app = Flask(__name__)


class Doc:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

# Function for the table of contents 
def toc(ctext):
    pattern = r"•\s*(.*?)\s*,?\s*page\s*(\d+)"
    headings = [
        {"title": match[0].strip(), "page_number": int(match[1])}
        for match in re.findall(pattern, ctext)
    ]
    return headings

def extracted_text(text):
    text = re.sub(r"[^\S\r\n]+", " ", text)
    return text.strip()

def ext_section(reader, heading, nexthead, toc_end_page):
    content = ""
    start_page = max(heading["page_number"] - 1, toc_end_page)
    end_page = nexthead["page_number"] - 1 if nexthead else reader.page_count

    for page_num in range(start_page, end_page):
        page = reader.load_page(page_num)
        page_text = page.get_text("text")
        if page_text:
            page_text = extracted_text(page_text)
            content += page_text + "\n"
    return content

# To load a PDF and process its contents
def process_pdf(file_path):
    reader = fitz.open(file_path)
    ctext = ""
    toc_end_page = 1
    for page_num in range(toc_end_page + 1):
        ctext += reader[page_num].get_text("text")
    # print("TOC Text:", ctext)
    headings = toc(ctext)
    # print("Headings:", headings)
    docs = []
    for i, heading in enumerate(headings):
        nexthead = headings[i + 1] if i + 1 < len(headings) else None
        content = ext_section(
            reader, heading, nexthead, toc_end_page
        )
        # print(f"Heading: '{heading['title']}':", content[:100])
        docs.append(Doc(content, metadata={"title": heading["title"]}))
    return docs

def process_documents():
    try:
        # Step 1: Load
        print("Loading")
        data = process_pdf("chapter9.pdf")
        embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)

        # Step 2: Transform and Step 3: Embed
        print("Processing " + str(len(data)) + " sections")
        if not data:
            print("No documents to store in the database.")
            return

        # Step 4: Store
        with MongoClient(
            params.mongodb_conn_string, tlsAllowInvalidCertificates=True
        ) as client:
            collection = client[params.db_name][params.collection_name]

            # if collection.count_documents({}) == 0:
            #     print("Adding data...")

            # Reset the collection and delete the existing documents
            collection.delete_many({})
            print("Existing data cleared.")

            # Insert the documents in MongoDB Atlas with their embedding
            MongoDBAtlasVectorSearch.from_documents(
                data, embeddings, collection=collection, index_name=params.index_name
            )
            print("Documents loaded and stored successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@app.route("/", methods=["GET"])
def index():
    return render_template("quest.html")


@app.route("/ask", methods=["GET"])
def ask_question():
    question = request.args.get("question")
    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    try:
        answer = get_answer(question)
        if "matches" in answer:
            matched_text = "<br>".join(answer["matches"])
        else:
            matched_text = "No matches found."

        return jsonify({"question": question, "answer": {"content": matched_text}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    process_documents()
    app.run(debug=True, use_reloader=False)























    # try:
    #     # Step 1: Load
    #     loaders = [
    #     WebBaseLoader("https://en.wikipedia.org/wiki/AT%26T"),
    #     WebBaseLoader("https://en.wikipedia.org/wiki/Bank_of_America")
    #     ]
    #     data = []
    #     for loader in loaders:
    #         data.extend(loader.load())

    #     # Step 2: Transform (Split)
    #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n\n", "\n", "(?<=\\. )", " "], length_function=len)
    #     docs = text_splitter.split_documents(data)
    #     print('Split into ' + str(len(docs)) + ' docs')
    #     # Step 3: Embed
    #     # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
    #     embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)

    #     # Step 4: Store
    #     # # Initialize MongoDB python client
    #     # try:
    #     #     client = MongoClient(params.mongodb_conn_string)

    #     with MongoClient(params.mongodb_conn_string, tlsAllowInvalidCertificates=True) as client:
    #         collection = client[params.db_name][params.collection_name]

    #         # Reset without deleting the Search Index
    #         collection.delete_many({})

    #         # Insert the documents in MongoDB Atlas with their embedding
    #         docsearch = MongoDBAtlasVectorSearch.from_documents(
    #             docs, embeddings, collection=collection, index_name=params.index_name
    #         )
    #     return jsonify({"message": "Documents loaded and stored successfully", "num_docs": len(docs)})

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500
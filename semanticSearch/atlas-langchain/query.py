import argparse
import warnings
from pymongo import MongoClient
import params
import re
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings


warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")

def get_answer(question):
    try:
        client = MongoClient(
            params.mongodb_conn_string, tlsAllowInvalidCertificates=True
        )
        db = client[params.db_name]
        collection = db[params.collection_name]

        if collection.estimated_document_count() == 0:
            # print("The collection is empty.")
            return {"error": "The collection is empty."}

        embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)
        query_embedding = embeddings.embed_query(question)

        vectorStore = MongoDBAtlasVectorSearch(
            collection, embeddings, index_name=params.index_name
        )

        docs = vectorStore.max_marginal_relevance_search(question, K=11)
        # print(f"Number of documents found: {len(docs)}")

        if len(docs) == 0:
            return {"error": "Not found."}

        question_keywords = question.lower().split()

        filtered_docs = []
        for doc in docs:
            try:
                doc_title = doc.metadata.get("title", "").lower()
                # print(doc_title)
                if any(keyword in doc_title for keyword in question_keywords):
                    doc_text = doc.page_content
                    filtered_docs.append({"title": doc_title, "text": doc_text})
            except AttributeError as e:
                print(f"An error occurred: {e}")

        if not filtered_docs:
            return {"error": "Not found with this title."}

        most_relevant_doc = filtered_docs[0]
        content = most_relevant_doc["text"]

        # pattern = r"RP/0/0/CPU0:router.*?# (.*)"
        pattern = r"(RP/0/0/CPU0:router.*?#(?:.*|$))"

        matches = re.findall(pattern, content)
        response = {"title": most_relevant_doc["title"], "matches": matches}
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Vector Search")
    parser.add_argument("-q", "--question", help="The question to ask", required=True)
    args = parser.parse_args()

    response = get_answer(args.question)

    print("\nResponse:")
    print("---------")
    if response is not None:
        if "error" not in response:
            print(f"Title: {response['title']}")
            if "matches" in response:
                for match in response["matches"]:
                    print(match)
            else:
                print("No matches found.")
        else:
            print(response["error"])
    else:
        print("No response")
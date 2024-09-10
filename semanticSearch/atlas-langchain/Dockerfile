FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

ENV OPENAI_API_KEY='sk-sAKCrOHCgygHTymp'
ENV MONGODB_CONN_STRING='mongodb+srv://prachisngrwl:<pass>@cluster0.dmxrhed.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ENV DB_NAME='search_db'
ENV COLLECTION_NAME='search_col'
ENV INDEX_NAME='vsearch_index'

# CMD ["python", "query.py", "--question", "What is AT&T?"]
CMD ["python", "vectorize.py"]

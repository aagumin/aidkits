from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
from aidkits.storage.opensearch_retriever import OpenSearchRetriever
from aidkits.models import LibrarySource

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False,
)

# Initialize the encoder
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Create the retriever
retriever = OpenSearchRetriever(client, encoder)

# Create a collection
retriever.create_collection("documentation")

# Upload a library
library = LibrarySource.from_json("path/to/library.json")
retriever.upload_library(library)

# Search for documents
results = retriever.search(
    question="How do I use the API?",
    collection_name="documentation",
    top_k=5
)

# Print the results
for result in results:
    print(result.markdown)
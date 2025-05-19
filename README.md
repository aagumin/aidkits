# Markdown Docs Crawler

`Markdown docs crawler` (command: `mdcrawler`) is a Python tool designed to parse Git repositories or local directories
containing Markdown files. It allows extracting content from Markdown files, organizing it into structured JSON, and
saving the output. This tool is particularly useful for processing documentation repositories.

---

## Features

- Clone remote Git repositories or work with local directories
- Extract and split Markdown content into chunks based on headers (`#`, `##`, `###`)
- Save parsed Markdown data in JSON format
- Index and retrieve chunks using OpenSearch
- Split large JSON files into multiple smaller files based on a grouping field
- Modular and extensible design
- Available as command-line utilities: `mdcrawler` and `jsonsplitter`

---

## Installation

Make sure you are using **Python 3.9 or newer** and have `pip` installed.

   ```bash
   pip install giga_crawler
   ```

Once installed, the command-line utility `giga_crawler` will be available.

---

## Usage

The tool works by taking a Git repository URL (or a local directory) and outputs a JSON file containing structured data
extracted from Markdown files.

### Command-line Arguments

| Argument                | Type    | Description                                                                                    |
|-------------------------|---------|------------------------------------------------------------------------------------------------|
| `--uri`                 | String  | URL of a remote Git repository to be cloned, or path to a local directory with Markdown files. |
| `--output_path`         | String  | Path to save the output JSON file. (Default: `output.json`)                                    |
| `--directory`           | String  | Optional. Path with docs source if used remote repo with clone.                                |
| `--multy_process`       | Boolean | Spawn multiple processes to speed up the process. (Default: `False`)                           |

#### OpenSearch Arguments

| Argument                | Type    | Description                                                                |
|-------------------------|---------|----------------------------------------------------------------------------|
| `--use_opensearch`      | Flag    | Use OpenSearch for indexing and retrieval.                                 |
| `--opensearch_host`     | String  | OpenSearch host. (Default: `localhost`)                                    |
| `--opensearch_port`     | Integer | OpenSearch port. (Default: `9200`)                                         |
| `--opensearch_index`    | String  | OpenSearch index name. (Default: `chunks`)                                 |
| `--opensearch_username` | String  | OpenSearch username. (Default: `admin`)                                    |
| `--opensearch_password` | String  | OpenSearch password. (Default: `admin`)                                    |
| `--opensearch_use_ssl`  | Flag    | Use SSL for OpenSearch connection.                                         |
| `--list_chunks`         | Flag    | List chunks from OpenSearch instead of indexing.                           |
| `--query`               | String  | Query string for searching chunks (used with `--list_chunks`).             |
| `--source_title`        | String  | Filter chunks by source title (used with `--list_chunks`).                 |
| `--size`                | Integer | Number of chunks to return (used with `--list_chunks`, default: `100`).    |
| `--from_`               | Integer | Starting offset for pagination (used with `--list_chunks`, default: `0`).  |

#### JSON Splitter Arguments

| Argument                | Type    | Description                                                                |
|-------------------------|---------|----------------------------------------------------------------------------|
| `--split_json`          | Flag    | Split a JSON file into multiple files based on a grouping field.           |
| `--json_input`          | String  | Path to the input JSON file to split (used with `--split_json`).           |
| `--json_output_dir`     | String  | Directory where the split JSON files will be saved (default: `output_by_title`). |
| `--json_group_by`       | String  | Field to group the data by (default: `title`).                             |
| `--json_encoding`       | String  | Encoding of the input JSON file (default: `utf-8`).                        |

### Examples

1. **Clone a remote repository and parse Markdown files:**

```bash
mdcrawler --uri https://github.com/example/repo.git
```
   or

```python
from crawler import MarkdownCrawler

MarkdownCrawler("repo/path").work()
```

   This will:
    - Clone the repository into a temporary directory
    - Parse all Markdown files in the repository
    - Save the JSON output to `output.json`

2. **Parse a local directory and save output to a custom JSON file:**

```bash
mdcrawler --uri ./local_directory --output_path result.json
```

   This will:
    - Use the specified local directory `./local_directory`
    - Parse all Markdown files in the directory
    - Save the JSON output to `result.json`

3. **Index chunks to OpenSearch:**

```bash
mdcrawler --uri ./local_directory --use_opensearch --opensearch_host localhost --opensearch_port 9200
```

   This will:
    - Parse all Markdown files in the directory
    - Save the JSON output to `output.json`
    - Index all chunks to OpenSearch

4. **Retrieve chunks from OpenSearch:**

```bash
mdcrawler --uri ./local_directory --list_chunks
```

   This will:
    - Connect to OpenSearch
    - Retrieve all chunks from the index
    - Display them in the console

5. **Search for specific chunks in OpenSearch:**

```bash
mdcrawler --uri ./local_directory --list_chunks --query "search term" --source_title "example.md"
```

   This will:
    - Connect to OpenSearch
    - Search for chunks containing "search term" in the content
    - Filter by source title "example.md"
    - Display the matching chunks in the console

6. **Split a JSON file into multiple files using mdcrawler:**

```bash
mdcrawler --uri ./local_directory --split_json --json_input large_file.json --json_output_dir output_directory --json_group_by title
```

   This will:
    - Read the large_file.json file
    - Group the data by the "title" field
    - Create a separate JSON file for each group in the output_directory
    - Display information about the created files

7. **Split a JSON file using the jsonsplitter command:**

```bash
jsonsplitter large_file.json --output-dir output_directory --group-by title
```

   This will:
    - Read the large_file.json file
    - Group the data by the "title" field
    - Create a separate JSON file for each group in the output_directory
    - Display information about the created files

### JSON Output Format

The JSON file saves structured data with the following format:

```json
[
  {
    "title": "example.md",
    "chunks": [
      {
        "title": "Header 1",
        "content": "Content under Header 1",
        "length": 120,
        "chunk_num": 1,
        "chunk_amount": 2
      },
      {
        "title": "Header 2",
        "content": "Content under Header 2",
        "length": 240,
        "chunk_num": 2,
        "chunk_amount": 2
      }
    ]
  }
]
```

---

## Advanced Usage

### OpenSearchRetriever

The `OpenSearchRetriever` class provides advanced vector search capabilities using OpenSearch. It allows you to:

- Search for documents based on semantic similarity
- Create and manage collections in OpenSearch
- Upload documents and libraries to OpenSearch

#### Example Usage

```python
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
from crawler.opensearch_retriever import OpenSearchRetriever
from crawler.models import LibrarySource

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
```

### DocumentationTool

The `DocumentationTool` class provides a high-level interface for answering questions using documentation stored in OpenSearch. It uses the `OpenSearchRetriever` to find relevant documentation and a language model to generate answers.

#### Example Usage

```python
from langchain_core.language_models import ChatOpenAI
from crawler.documentation_tool import DocumentationTool
from crawler.opensearch_retriever import OpenSearchRetriever

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Initialize the retriever (as shown above)
# ...

# Create the documentation tool
doc_tool = DocumentationTool(
    llm=llm,
    retriever=retriever,
    collection_name="documentation",
    top_k=5
)

# Answer a question
answer = doc_tool.invoke({"question": "How do I use the API?"})
print(answer)
```

### JsonSplitter

The `JsonSplitter` class provides functionality for splitting a large JSON file into multiple smaller files based on a grouping field. It can be used to organize JSON data by a common field, making it easier to work with large datasets.

#### Example Usage

```python
from crawler.json_splitter import JsonSplitter

# Create a JsonSplitter instance
splitter = JsonSplitter(output_dir="output_directory")

# Split a JSON file
grouped_data = splitter.split_json_file(
    input_file="large_file.json",
    group_by_field="title",
    encoding="utf-8"
)

# Print information about the created files
print(f"Total files created: {len(grouped_data)}")

# You can also split JSON data directly
data = [
    {"title": "Document 1", "content": "Content 1"},
    {"title": "Document 2", "content": "Content 2"},
    {"title": "Document 1", "content": "More content for Document 1"}
]

grouped_data = splitter.split_json_data(
    data=data,
    group_by_field="title"
)

# This will create two files:
# - output_directory/Document_1.json (containing 2 items)
# - output_directory/Document_2.json (containing 1 item)
```

---

## Development

If you want to contribute or modify this package, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/aagumin/twin-crawler.git
   cd docs-crawler
   ```

2. Install the package in editable mode with development dependencies:

   ```bash
   pip install -e .[dev]
   ```

3. Run the package locally for testing:

   ```bash
   python -m giga_crawler.main --repo_url ./local_directory --output_path test_output.json
   ```

---

## Dependencies

The project requires the following Python packages:

- **Pydantic**: For modeling and validation of JSON data.
- **GitPython**: For working with Git repositories.
- **opensearch-py**: For interacting with OpenSearch.
- **sentence-transformers**: For encoding text into vectors for semantic search.
- **langchain-core**: For language model integration and output parsing.

All dependencies are automatically installed when you use `pip install`.

---

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository and create a branch for your feature or bug fix.
2. Write clear, concise code and include comments where necessary.
3. Submit a pull request with a detailed explanation of your changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

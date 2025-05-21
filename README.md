# AI (Documentation) Kit

`AIDkit` is a Python tools collection designed to help create AI documentation assistants. It includes utilities for parsing Git repositories or local directories containing Markdown files, extracting content, organizing it into structured JSON, and saving the output. These tools are particularly useful for processing documentation repositories for AI-powered assistance. `aidkit`

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
   pip install aidkit
   ```

Once installed, the command-line utility `giga_crawler` will be available.

---

## Usage

The tool works by taking a Git repository URL (or a local directory) and outputs a JSON file containing structured data
extracted from Markdown files.

### Command-line Arguments

| Argument          | Type    | Description                                                                                    |
|-------------------|---------|------------------------------------------------------------------------------------------------|
| `--uri`           | String  | URL of a remote Git repository to be cloned, or path to a local directory with Markdown files. |
| `--output_path`   | String  | Path to save the output JSON file. (Default: `output.json`)                                    |
| `--directory`     | String  | Optional. Path with docs source if used remote repo with clone.                                |
| `--multy_process` | Boolean | Spawn multiple processes to speed up the process. (Default: `False`)                           |

### Examples

1. **Clone a remote repository and parse Markdown files:**

```bash
aidkit parse --uri https://github.com/example/repo.git
```

or

```python
from aidkits import MarkdownCrawler

MarkdownCrawler("repo/path").work()
```

This will:
- Clone the repository into a temporary directory
- Parse all Markdown files in the repository
- Save the JSON output to `output.json`

2. **Parse a local directory and save output to a custom JSON file:**

```bash
aidkit parse --uri ./local_directory --output_path result.json
```

This will:
- Use the specified local directory `./local_directory`
- Parse all Markdown files in the directory
- Save the JSON output to `result.json`

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
```

### DocumentationTool

The `DocumentationTool` class provides a high-level interface for answering questions using documentation stored in
OpenSearch. It uses the `OpenSearchRetriever` to find relevant documentation and a language model to generate answers.

#### Example Usage

```python
from langchain_core.language_models import ChatOpenAI
from aidkits.documentation_tool import DocumentationTool
from aidkits.storage.opensearch_retriever import OpenSearchRetriever

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

The `JsonSplitter` class provides functionality for splitting a large JSON file into multiple smaller files based on a
grouping field. It can be used to organize JSON data by a common field, making it easier to work with large datasets.

#### Example Usage

```python
from aidkits.json_splitter import JsonSplitter

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

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository and create a branch for your feature or bug fix.
2. Write clear, concise code and include comments where necessary.
3. Submit a pull request with a detailed explanation of your changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

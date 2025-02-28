# Markdown Docs Crawler

`Markdown docs crawler` (command: `mdcrawler`) is a Python tool designed to parse Git repositories or local directories
containing Markdown files. It allows extracting content from Markdown files, organizing it into structured JSON, and
saving the output. This tool is particularly useful for processing documentation repositories.

---

## Features

- Clone remote Git repositories or work with local directories
- Extract and split Markdown content into chunks based on headers (`#`, `##`, `###`)
- Save parsed Markdown data in JSON format
- Modular and extensible design
- Available as a command-line utility: `mdcrawler`

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

| Argument        | Type   | Description                                                                                    |
|-----------------|--------|------------------------------------------------------------------------------------------------|
| `--repo_url`    | String | URL of a remote Git repository to be cloned, or path to a local directory with Markdown files. |
| `--output_path` | String | Path to save the output JSON file. (Default: `output.json`)                                    |
| `--path_prefix` | String | Optional. Path with docs source if used remote repo with clone.                                |

### Examples

1. **Clone a remote repository and parse Markdown files:**

```bash
mdcrawler --repo_url https://github.com/example/repo.git --is_remote
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
   giga_crawler --repo_url ./local_directory --output_path result.json
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

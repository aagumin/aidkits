import argparse
from pathlib import Path

from crawler.parse import MarkdownCrawler
from crawler.storage import MdLocation
from crawler.opensearch import OpenSearchClient
from crawler.json_splitter import JsonSplitter


def main():
    parser = argparse.ArgumentParser(
        description="Git repository parser with markdown data extraction.",
    )
    parser.add_argument(
        "--uri",
        type=str,
        required=True,
        help="URL comma-separated URLs of the repository to clone or the path to a local directory. Add a path prefix to the local directory.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="output.json",
        help="Path to save the JSON output (default: output.json).",
    )

    parser.add_argument(
        "--directory",
        type=str,
        default="",
        help="Path to save the JSON output (default: output.json).",
    )

    parser.add_argument(
        "--multy_process",
        type=bool,
        default=False,
        help="Spawn multiple processes to speed up the process.",
    )

    # OpenSearch arguments
    parser.add_argument(
        "--use_opensearch",
        action="store_true",
        help="Use OpenSearch for indexing and retrieval.",
    )
    parser.add_argument(
        "--opensearch_host",
        type=str,
        default="localhost",
        help="OpenSearch host (default: localhost).",
    )
    parser.add_argument(
        "--opensearch_port",
        type=int,
        default=9200,
        help="OpenSearch port (default: 9200).",
    )
    parser.add_argument(
        "--opensearch_index",
        type=str,
        default="chunks",
        help="OpenSearch index name (default: chunks).",
    )
    parser.add_argument(
        "--opensearch_username",
        type=str,
        default="admin",
        help="OpenSearch username (default: admin).",
    )
    parser.add_argument(
        "--opensearch_password",
        type=str,
        default="admin",
        help="OpenSearch password (default: admin).",
    )
    parser.add_argument(
        "--opensearch_use_ssl",
        action="store_true",
        help="Use SSL for OpenSearch connection.",
    )
    parser.add_argument(
        "--list_chunks",
        action="store_true",
        help="List chunks from OpenSearch instead of indexing.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Query string for searching chunks (used with --list_chunks).",
    )
    parser.add_argument(
        "--source_title",
        type=str,
        default=None,
        help="Filter chunks by source title (used with --list_chunks).",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=100,
        help="Number of chunks to return (used with --list_chunks, default: 100).",
    )
    parser.add_argument(
        "--from_",
        type=int,
        default=0,
        help="Starting offset for pagination (used with --list_chunks, default: 0).",
    )

    # JSON Splitter arguments
    json_splitter_group = parser.add_argument_group('JSON Splitter', 'Arguments for splitting JSON files')
    json_splitter_group.add_argument(
        "--split_json",
        action="store_true",
        help="Split a JSON file into multiple files based on a grouping field.",
    )
    json_splitter_group.add_argument(
        "--json_input",
        type=str,
        help="Path to the input JSON file to split (used with --split_json).",
    )
    json_splitter_group.add_argument(
        "--json_output_dir",
        type=str,
        default="output_by_title",
        help="Directory where the split JSON files will be saved (used with --split_json, default: output_by_title).",
    )
    json_splitter_group.add_argument(
        "--json_group_by",
        type=str,
        default="title",
        help="Field to group the data by (used with --split_json, default: title).",
    )
    json_splitter_group.add_argument(
        "--json_encoding",
        type=str,
        default="utf-8",
        help="Encoding of the input JSON file (used with --split_json, default: utf-8).",
    )

    args = parser.parse_args()
    repo_url = list(map(str.strip, args.uri.split(",")))
    directory = list(map(str.strip, args.directory.split(",")))
    output_path = args.output_path

    # Create OpenSearch client if list_chunks is requested
    opensearch_client = None
    if args.list_chunks:
        opensearch_client = OpenSearchClient(
            host=args.opensearch_host,
            port=args.opensearch_port,
            username=args.opensearch_username,
            password=args.opensearch_password,
            index_name=args.opensearch_index,
            use_ssl=args.opensearch_use_ssl,
            verify_certs=False,
        )

    # If split_json flag is provided, split the JSON file
    if args.split_json:
        if not args.json_input:
            print("Error: --json_input is required when using --split_json")
            return 1

        print(f"Splitting JSON file: {args.json_input}")
        print(f"Output directory: {args.json_output_dir}")
        print(f"Grouping by field: {args.json_group_by}")

        try:
            splitter = JsonSplitter(output_dir=args.json_output_dir)
            grouped_data = splitter.split_json_file(
                input_file=args.json_input,
                group_by_field=args.json_group_by,
                encoding=args.json_encoding
            )
            print(f"\nTotal files created: {len(grouped_data)}")
        except Exception as e:
            print(f"Error splitting JSON file: {str(e)}")
            return 1
    # If list_chunks flag is provided, retrieve and print chunks from OpenSearch
    elif args.list_chunks and opensearch_client:
        print(f"Retrieving chunks from OpenSearch index '{args.opensearch_index}'...")
        chunks = opensearch_client.retrieve_chunks(
            query=args.query,
            source_title=args.source_title,
            size=args.size,
            from_=args.from_
        )

        if chunks:
            print(f"Found {len(chunks)} chunks:")
            for i, chunk in enumerate(chunks, 1):
                print(f"\n--- Chunk {i} ---")
                print(f"Title: {chunk['title']}")
                print(f"Source: {chunk['source_title']}")
                print(f"Chunk: {chunk['chunk_num']}/{chunk['chunk_amount']}")
                print(f"Length: {chunk['length']}")
                print(f"Content: {chunk['content'][:200]}..." if len(chunk['content']) > 200 else f"Content: {chunk['content']}")
        else:
            print("No chunks found matching the criteria.")
    else:
        # Process repositories and index to OpenSearch
        for repo, folder in zip(repo_url, directory):
            repo_with_md = MdLocation(repo).define()
            local_repo = repo_with_md.fetch()

            translation_table = dict.fromkeys(map(ord, "@:/."), "_")
            crawler = MarkdownCrawler(
                local_repo,
                f"{Path(repo.translate(translation_table)).as_posix()}" + output_path,
                folder,
            )
            print("going to work")
            crawler.work()

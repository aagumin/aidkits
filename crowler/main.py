import argparse
import json
import shutil
from pathlib import Path

from crowler.parse import clone_git_repo, collect_markdown_files

def main():
    parser = argparse.ArgumentParser(description="Git repository parser with markdown data extraction.")
    parser.add_argument(
        "--repo_url", type=str, required=True,
        help="URL of the repository to clone or the path to a local directory."
    )
    parser.add_argument(
        "--output_path", type=str, default="output.json",
        help="Path to save the JSON output (default: output.json)."
    )
    parser.add_argument(
        "--path_prefix",
        help="Path with docs for remote repo (optional).",
    )
    args = parser.parse_args()
    repo_url = args.repo_url
    output_path = args.output_path
    path_prefix = args.path_prefix

    is_remote = True if any(repo_url.startswith(prefix) for prefix in ["https://", "http://", "git@", "ssh://"]) else False

    try:
        if is_remote:
            directory_path = clone_git_repo(repo_url)
        else:
            directory_path = repo_url

        if path_prefix:  # Выполнять только если path_prefix не равен None
            directory_path = Path(directory_path) / path_prefix

        library_sources = collect_markdown_files(directory_path)
        if library_sources:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    [lib_source.model_dump() for lib_source in library_sources],
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
            print(f"JSON saved: {output_path}")

        if library_sources and library_sources[0].chunks:
            print(library_sources[0].chunks[0].markdown)

    finally:
        if is_remote:
            shutil.rmtree(directory_path)
            print(f"Temporary directory {directory_path} removed.")

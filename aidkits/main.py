import argparse
from pathlib import Path

from aidkits.parse import MarkdownCrawler
from aidkits.storage import MdLocation
from aidkits.json_splitter import JsonSplitter


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

    args = parser.parse_args()
    repo_url = list(map(str.strip, args.uri.split(",")))
    directory = list(map(str.strip, args.directory.split(",")))
    output_path = args.output_path

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

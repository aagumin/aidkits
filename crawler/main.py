import argparse

from crawler.parse import MarkdownCrawler


def main():
    parser = argparse.ArgumentParser(
        description="Git repository parser with markdown data extraction.",
    )
    parser.add_argument(
        "--repo_url",
        type=str,
        required=True,
        help="URL of the repository to clone or the path to a local directory.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="output.json",
        help="Path to save the JSON output (default: output.json).",
    )
    parser.add_argument(
        "--path_prefix",
        help="Path with docs for remote repo (optional).",
    )

    args = parser.parse_args()
    repo_url = args.repo_url
    output_path = args.output_path
    path_prefix = args.path_prefix

    crawler = MarkdownCrawler(repo_url, output_path, path_prefix)
    crawler.work()

import shutil

from aidkits import MarkdownCrawler
from aidkits.sources import MdLocation

REPO_WITH_MD="/test"

repo_with_md = MdLocation(REPO_WITH_MD).define()
repo = repo_with_md.fetch()

if __name__ == "__main__":
    crawler = MarkdownCrawler(repo)
    crawler.work()
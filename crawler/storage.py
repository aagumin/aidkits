import shutil
import tempfile
import typing
from pathlib import Path

from git import Repo


class Location(typing.Protocol):
    def __init__(self, uri: str):
        self.uri = uri

    def fetch(self):
        raise NotImplementedError


class LocalFileSystem:
    def __init__(self, uri: str):
        self.uri = uri

    def fetch(self) -> str:
        """Clones a Git repository from the given URL into a temporary directory.

        :param repo_url: URL of the repository (GitHub, Bitbucket, or other remote repositories)
        :return: The path to the temporary directory where the repository was cloned
        """
        validated_path = Path(self.uri)
        if not all({validated_path.exists(), validated_path.is_dir()}):
            raise ValueError("Invalid repository URL")

        return self.uri


class RemoteGitRepository:
    def __init__(self, uri: str):
        self.uri = uri

    def fetch(self) -> str:
        """Clones a Git repository from the given URL into a temporary directory.

        :param repo_url: URL of the repository (GitHub, Bitbucket, or other remote repositories)
        :return: The path to the temporary directory where the repository was cloned
        """
        temp_dir = tempfile.mkdtemp()
        try:
            print(f"Cloning repository {self.uri} into {temp_dir}...")
            Repo.clone_from(self.uri, temp_dir)
            return temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir)
            raise RuntimeError(f"Failed to clone repository: {e}")

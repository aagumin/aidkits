import shutil
import tempfile
import typing
from functools import cached_property
from pathlib import Path

from git import Repo


class Location(typing.Protocol):
    def __init__(self, uri: str):
        self.uri = uri

    def fetch(self) -> str:
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
            raise e


class S3FileSystem:
    def __init__(self, uri: str):
        self.uri = uri

    def fetch(self) -> str:
        return ""


class MdLocation:
    def __init__(self, uri: str):
        self.repo_url = uri

        self.tmp_dir = None

    @cached_property
    def _is_remote(self) -> bool:
        is_remote = (
            True
            if any(
                self.repo_url.startswith(prefix)
                for prefix in ["https://", "http://", "git@", "ssh://"]
            )
            else False
        )
        return is_remote

    @cached_property
    def _is_s3(self) -> bool:
        return self.repo_url.startswith("s3://")

    def define(self) -> type[Location]:
        if self._is_remote:
            return RemoteGitRepository(self.repo_url)
        elif self._is_s3:
            return S3FileSystem(self.repo_url)
        else:
            return LocalFileSystem(self.repo_url)

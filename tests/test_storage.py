import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from git import GitCommandError

from aidkits.storage import LocalFileSystem, RemoteGitRepository


def test_remote_git_repository_fetch_with_valid_uri():
    valid_uri = "https://github.com/sample/repo.git"
    with patch("crawler.storage.Repo.clone_from") as mock_clone:
        mock_clone.return_value = None
        remote_repo = RemoteGitRepository(uri=valid_uri)
        temp_dir = remote_repo.fetch()
        assert os.path.isdir(temp_dir)
        mock_clone.assert_called_once_with(valid_uri, temp_dir)


def test_remote_git_repository_fetch_with_invalid_uri(capsys):
    invalid_uri = "invalid_git_url"
    remote_repo = RemoteGitRepository(uri=invalid_uri)
    with pytest.raises(GitCommandError):
        remote_repo.fetch()
    # captured = capsys.readouterr()
    # assert captured.err == "fatal: repository 'invalid_git_url' does not exist"


def test_remote_git_repository_cleans_up_on_failure():
    faulty_uri = "https://github.com/nonexistent/repo.git"
    with patch(
        "crawler.storage.Repo.clone_from",
        side_effect=Exception("Error cloning"),
    ):
        remote_repo = RemoteGitRepository(uri=faulty_uri)
        with patch("shutil.rmtree") as mock_rmtree:
            with pytest.raises(
                Exception,
                match="Error cloning",
            ):
                remote_repo.fetch()
            mock_rmtree.assert_called_once()


def test_local_file_system_fetch_with_valid_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        lfs = LocalFileSystem(uri=temp_dir)
        result = lfs.fetch()
        assert result == temp_dir


def test_local_file_system_fetch_with_invalid_path():
    invalid_path = str(Path(tempfile.gettempdir()) / "non_existent_dir")
    lfs = LocalFileSystem(uri=invalid_path)
    with pytest.raises(ValueError, match="Invalid repository URL"):
        lfs.fetch()


def test_local_file_system_fetch_with_file_instead_of_directory():
    with tempfile.NamedTemporaryFile() as temp_file:
        lfs = LocalFileSystem(uri=temp_file.name)
        with pytest.raises(ValueError, match="Invalid repository URL"):
            lfs.fetch()

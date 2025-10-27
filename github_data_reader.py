from typing import Iterable, Callable, List
from dataclasses import dataclass
import zipfile
import requests
import io
import traceback


@dataclass
class RawRepositoryFile:
    filename: str
    content: str

class GithubRepositoryDataReader:
    def __init__(self, 
                 repo_owner: str,
                 repo_name: str,
                 allowed_extensions: Iterable[str] | None = None,
                 filename_filter: Callable[[str], bool] | None = None
        ):
        prefix = "https://codeload.github.com"
        self.url = (
            f"{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main"
        )

        if allowed_extensions is not None:
            self.allowed_extensions = {ext.lower() for ext in allowed_extensions}

        if filename_filter is None:
            self.filename_filter = lambda filepath: True
        else:
            self.filename_filter = filename_filter

    def read(self) -> list[RawRepositoryFile]:
        resp = requests.get(self.url)
        if resp.status_code != 200:
            raise Exception(f"Failed to download repository: {resp.status_code}")

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        repository_data = self._extract_files(zf)
        zf.close()

        return repository_data
    
    def _extract_files(self, zf: zipfile.ZipFile) -> list[RawRepositoryFile]:
        data = []

        for file_info in zf.infolist():
            filepath = self._normalize_filepath(file_info.filename)

            if self._should_skip_file(filepath):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode("utf-8", errors="ignore")
                    if content is not None:
                        content = content.strip()

                    file = RawRepositoryFile(
                        filename=filepath,
                        content=content
                    )
                    data.append(file)

            except Exception as e:
                print(f"Error processing {file_info.filename}: {e}")
                traceback.print_exc()
                continue

        return data

    def _should_skip_file(self, filepath: str) -> bool:
        filepath = filepath.lower()

        # directory
        if filepath.endswith("/"):
            return True

        # hidden file
        filename = filepath.split("/")[-1]
        if filename.startswith("."):
            return True

        if self.allowed_extensions:
            ext = self._get_extension(filepath)
            if ext not in self.allowed_extensions:
                return True

        if not self.filename_filter(filepath):
            return True

        return False

    def _get_extension(self, filepath: str) -> str:
        filename = filepath.lower().split("/")[-1]
        if "." in filename:
            return filename.rsplit(".", maxsplit=1)[-1]
        else:
            return ""

    def _normalize_filepath(self, filepath: str) -> str:
        parts = filepath.split("/", maxsplit=1)
        if len(parts) > 1:
            return parts[1]
        else:
            return parts[0]

def read_github_data(repo_owner: str, repo_name: str,  ) -> List[RawRepositoryFile]:
    allowed_extensions = {"chordpro"}

    reader = GithubRepositoryDataReader(
        repo_owner,
        repo_name,
        allowed_extensions=allowed_extensions,
    )
    
    return reader.read()
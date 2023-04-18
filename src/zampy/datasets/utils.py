"""Shared utilities from datasets."""
import urllib.request
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm


class TqdmUpdate(tqdm):
    """Wrap a tqdm progress bar to be updateable by urllib.request.urlretrieve."""
    def update_to(self, b: int = 1, bsize: int = 1, tsize: Optional[int] = None):
        """Update the progress bar.

        Args:
            b: Number of blocks transferred so far.
            bsize: Size of each block (in tqdm units).
            tsize: Total size (in tqdm units). If `None`, remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)


def download_url(url: str, fpath: Path, overwrite: bool) -> None:
    """Download a URL, and display a progress bar for that file.

    Args:
        url: URL to be downloaded.
        fpath: File path to which the URL should be saved.
        overwrite: If an existing file (of the same size!) should be overwritten.
    """
    if get_file_size(fpath) != get_url_size(url) or overwrite:
        with TqdmUpdate(
            unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]
        ) as t:
            urllib.request.urlretrieve(url, filename=fpath, reporthook=t.update_to)
    else:
        print(f"File '{fpath.name}' already exists, skipping...")


def get_url_size(url: str) -> int:
    """Return the size (bytes) of a given URL."""
    response = requests.head(url)
    return int(response.headers["Content-Length"])


def get_file_size(fpath: Path) -> int:
    """Return the size (bytes) of a given Path."""
    if not fpath.exists():
        return 0
    else:
        return fpath.stat().st_size

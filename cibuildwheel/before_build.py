import os
import sys
import importlib.util
import urllib.request
from pathlib import Path

def get_pyside6_path():
    """Determine the path to the PySide6 folder."""
    spec = importlib.util.find_spec("PySide6")
    if spec is None:
        print("PySide6 is not installed.")
        sys.exit(1)
    return Path(spec.origin).parent

def get_qt_version():
    """Determine the Qt version."""
    try:
        from PySide6 import __version__
        return '.'.join(__version__.split('.')[:3])
    except ImportError:
        print("Failed to import PySide6 or get its version.")
        sys.exit(1)

def download_file(url, save_path):
    """Download a file from a given URL and save it to the specified path."""
    print(f"Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Successfully downloaded to {save_path}")
    except urllib.error.URLError as e:
        print(f"Error downloading {url}: {e}")
        return False
    return True

def download_pyside_cgit_doc(doc_dir, qt_version):
    """Download specific documentation files."""
    base_url = f"https://code.qt.io/cgit/pyside/pyside-setup.git/plain/sources/pyside6/PySide6/doc"
    files = [
        "qtqml_functions.rst",
        "qtquicktest.rst",
        "qtuitools.rst"
    ]
    
    for file in files:
        url = f"{base_url}/{file}?h={qt_version}"
        save_path = doc_dir / file
        download_file(url, save_path)

def main():
    pyside6_path = get_pyside6_path()
    print(f"PySide6 path: {pyside6_path}")

    qt_version = get_qt_version()
    print(f"Qt version: {qt_version}")

    doc_dir = pyside6_path / "doc"
    doc_dir.mkdir(parents=True, exist_ok=True)

    if qt_version == "6.7.2":
        print(f"Downloading documentation for Qt version {qt_version}")
        download_pyside_cgit_doc(doc_dir, qt_version)

if __name__ == "__main__":
    main()
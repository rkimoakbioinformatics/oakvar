from typing import Optional
from typing import Tuple
from pathlib import Path


def download(
    url=None,
    fpath=None,
    directory=None,
    system_worker_state=None,
    check_install_kill=None,
    module_name=None,
    total_size=0,
    cur_size=0,
    kind: str = "file",
    outer=None,
):
    from .download_library import download as download_util

    if not url or (not fpath and not directory):
        return
    if "drive.google.com" in url:
        import gdown

        gdown.download(url=url, output=fpath, quiet=True, fuzzy=True)
    elif "github.com" in url:
        if not directory:
            raise Exception("directory should be given.")
        download_from_github(url, directory, outer=outer)
    else:
        download_util(
            url,
            fpath,
            kind="file",
            file_kind=kind,
            verbose=False,
            replace=True,
            system_worker_state=system_worker_state,
            check_install_kill=check_install_kill,
            module_name=module_name,
            total_size=total_size,
            cur_size=cur_size,
            outer=outer,
        )


def is_git_repo_url(url: str) -> Optional[Tuple]:
    from re import compile

    ptn = compile(r"^https?://(?:www\.)?github\.com/([\w-]+)/([\w-]+)$")
    m = ptn.search(url)
    if not m:
        return None
    else:
        owner, repo = m.groups()
        return owner, repo


def is_git_branch_url(url: str):
    from re import compile

    ptn = compile(r"https?://(?:www\.)?github\.com/([\w-]+)/([\w-]+)/tree/([\w-]+)$")
    m = ptn.search(url)
    if not m:
        return None
    else:
        owner, repo, branch = m.groups()
        return owner, repo, branch


def is_git_branch_folder(url: str):
    from re import compile

    ptn = compile(
        r"https?://(?:www\.)?github\.com/([\w-]+)/([\w-]+)/tree/([\w-]+)/([/\w-]+)"
    )
    m = ptn.search(url)
    if not m:
        return None
    else:
        owner, repo, branch, folder = m.groups()
        return owner, repo, branch, folder


def download_github_repo(owner: str, repo: str, directory: str, outer=None):
    download_github_branch(owner, repo, "master", directory, outer=outer)


def download_github_branch(
    owner: str, repo: str, branch: str, directory: str, outer=None
):
    download_github_branch_folder(owner, repo, branch, "", directory, outer=outer)


def download_github_branch_folder(
    owner: str, repo: str, branch: str, folder: str, directory: str, outer=None
):
    from pathlib import Path

    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}?ref={branch}"
    )
    install_dir = Path(directory)
    download_git_folder(api_url, folder, install_dir, outer=outer)


def download_from_github(url: str, directory: str, outer=None):
    g = is_git_repo_url(url)
    if g and directory:
        owner, repo = g
        download_github_repo(owner, repo, directory, outer=outer)
        return
    g = is_git_branch_url(url)
    if g and directory:
        owner, repo, branch = g
        download_github_branch(owner, repo, branch, directory, outer=outer)
        return
    g = is_git_branch_folder(url)
    if g and directory:
        owner, repo, branch, folder = g
        download_github_branch_folder(
            owner, repo, branch, folder, directory, outer=outer
        )
        return
    if url.endswith(".zip"):
        path = Path(url).name
        download_git_file(url, path, Path(directory), outer=outer)
        return


def download_git_folder(url: str, path: str, install_dir: Path, outer=None):
    from requests import get

    res = get(url)
    data = res.json()
    if isinstance(data, dict) and data.get("type") == "file":
        download_git_file(data["download_url"], data["path"], install_dir, outer=outer)
        return
    folder_p = install_dir / path
    if not folder_p.exists():
        folder_p.mkdir(parents=True, exist_ok=True)
    for el in data:
        ty = el["type"]
        path = el["path"]
        if ty == "dir":
            download_git_folder(el["url"], path, install_dir, outer=outer)
        elif ty == "file":
            download_git_file(el["download_url"], path, install_dir, outer=outer)


def download_git_file(url: str, path: str, install_dir: Path, outer=None):
    import download as download_util

    # if search(r"\.zip[0-9]*$", url):
    #    download_util.download(
    #        url,
    #        str(install_dir),
    #        kind="file",
    #        verbose=False,
    #        replace=True,
    #    )
    # else:
    if outer:
        outer.write(f"getting {url}...")
    download_util.download(
        url,
        str(install_dir / path),
        kind="file",
        verbose=False,
        replace=True,
    )


def is_url(url):
    from re import compile

    url_pattern = compile("^(http|https)://.*$")
    match = url_pattern.match(url)
    return match is not None


def is_zip_path(url):
    from pathlib import Path

    p = Path(url)
    return p.exists() and p.suffix == ".zip"

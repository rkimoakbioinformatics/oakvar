def download(url, fpath):
    import download as download_util
    import gdown

    if "drive.google.com" in url:
        gdown.download(url=url, output=fpath, quiet=True, fuzzy=True)
    elif "github.com" in url:
        download_git_folder(url=url, install_dir=fpath)
    else:
        download_util.download(url, fpath, kind="file", verbose=False, replace=True)


def download_git_file(el, folder):
    import download as download_util
    from re import search
    if search(r"\.zip[0-9]*$", el["download_url"]):
        download_util.download(el["download_url"], str(folder), kind="file", verbose=False, replace=True)
    else:
        download_util.download(el["download_url"], str(folder / el["name"]), kind="file", verbose=False, replace=True)

def get_git_api_url(url):
    from re import compile
    branch_re = compile("/(tree|blob)/(.+?)/")
    branch_match = branch_re.search(url)
    if not branch_match:
        return None
    url_1 = url[:branch_match.start()].replace("github.com", "api.github.com/repos", 1)
    url_2 = "contents"
    url_3 = url[branch_match.end():]
    branch = branch_match.group(2)
    api_url = f"{url_1}/{url_2}/{url_3}?ref={branch}"
    return api_url

def download_git_folder(url=None, install_dir=None):
    from requests import get
    from pathlib import Path
    if not url or not install_dir:
        return
    if not isinstance(install_dir, Path):
        install_dir = Path(install_dir)
    api_url = get_git_api_url(url)
    if not api_url:
        return
    res = get(api_url)
    data = res.json()
    if isinstance(data, dict) and data.get("type") == "file":
        download_git_file(data, install_dir)
        return
    folder = install_dir / Path(url).stem
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    for el in data:
        if el["type"] == "dir":
            download_git_folder(url=el["html_url"], install_dir=folder)
        elif el["type"] == "file":
            download_git_file(el, folder)

def is_url(url):
    from re import compile
    url_pattern = compile("^(http|https)://.*$")
    match = url_pattern.match(url)
    return match is not None

def is_zip_path(url):
    from pathlib import Path
    p = Path(url)
    return p.exists() and p.suffix == ".zip"


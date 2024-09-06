# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Copy of https://github.com/choldgraf/download
"""Utilities to download a file. Heavily copied from MNE-python."""

from typing import Optional
import os
import os.path as op
from six.moves import urllib  # type: ignore
from zipfile import ZipFile
import tarfile
from math import log
import sys
import shutil
import tempfile
import ftplib
from functools import partial

ALLOWED_KINDS = ["file", "tar", "zip", "tar.gz"]
ZIP_KINDS = ["tar", "zip", "tar.gz"]


def download(
    url,
    path,
    kind="file",
    file_kind: str = "file",
    progressbar=True,
    replace=False,
    timeout=10.0,
    verbose=True,
    system_worker_state=None,
    check_install_kill=None,
    module_name=None,
    total_size=0,
    cur_size=0,
    outer=None,
):
    """Download a URL.

    This will download a file and store it in a '~/data/` folder,
    creating directories if need be. It will also work for zip
    files, in which case it will unzip all of the files to the
    desired location.

    Parameters
    ----------
    url : string
        The url of the file to download. This may be a dropbox
        or google drive "share link", or a regular URL. If it
        is a share link, then it should point to a single file and
        not a folder. To download folders, zip them first.
    path : string
        The path where the downloaded file will be stored. If ``zipfile``
        is True, then this must be a folder into which files will be zipped.
    kind : one of ['file', 'zip', 'tar', 'tar.gz']
        The kind of file to be downloaded. If not 'file', then the file
        contents will be unpackaged according to the kind specified. Package
        contents will be placed in ``root_destination/<name>``.
    progressbar : bool
        Whether to display a progress bar during file download.
    replace : bool
        If True and the URL points to a single file, overwrite the
        old file if possible.
    timeout : float
        The URL open timeout.
    verbose : bool
        Whether to print download status to the screen.

    Returns
    -------
    out_path : string
        A path to the downloaded file (or folder, in the case of
        a zip file).
    """
    assert module_name is not None
    if kind not in ALLOWED_KINDS:
        raise ValueError("`kind` must be one of {}, got {}".format(ALLOWED_KINDS, kind))

    # Make sure we have directories to dump files
    path = op.expanduser(path)

    if len(path) == 0:
        raise ValueError("You must specify a path. For current directory use .")

    download_url = _convert_url_to_downloadable(url)

    if replace is False and op.exists(path):
        msg = (
            "Replace is False and data exists, so doing nothing. "
            "Use replace=True to re-download the data."
        )
    elif kind in ZIP_KINDS:
        # Create new folder for data if we need it
        if path and not op.isdir(path):
            if verbose and outer:
                outer.write("Creating data folder...")
            os.makedirs(path)

        # Download the file to a temporary folder to unzip
        path_temp = _TempDir()
        path_temp_file = op.join(path_temp, "tmp.{}".format(kind))
        _fetch_file(
            download_url,
            path_temp_file,
            file_kind,
            timeout=timeout,
            verbose=verbose,
            progressbar=progressbar,
            system_worker_state=system_worker_state,
            check_install_kill=check_install_kill,
            module_name=module_name,
            outer=outer,
        )

        # Unzip the file to the out path
        if verbose and outer:
            outer.write(f"Extracting {kind} file...")
        if kind == "zip":
            zipper = ZipFile
        elif kind == "tar":
            zipper = tarfile.open
        elif kind == "tar.gz":
            zipper = partial(tarfile.open, mode="r:gz")
        else:
            raise
        with zipper(path_temp_file) as myobj:
            myobj.extractall(path)
        msg = "Successfully downloaded / unzipped to {}".format(path)
    else:
        directory = op.dirname(path)
        if directory and not op.isdir(directory):
            os.makedirs(directory)
        _fetch_file(
            download_url,
            path,
            file_kind,
            timeout=timeout,
            verbose=verbose,
            progressbar=progressbar,
            system_worker_state=system_worker_state,
            check_install_kill=check_install_kill,
            module_name=module_name,
            cur_size=cur_size,
            total_size=total_size,
            outer=outer,
        )
        msg = "Successfully downloaded file to {}".format(path)
    if verbose and outer:
        outer.write(msg)
    return path


def _convert_url_to_downloadable(url):
    """Convert a url to the proper style depending on its website."""

    if "drive.google.com" in url:
        # For future support of google drive
        file_id = url.split("d/")[1].split("/")[0]
        base_url = "https://drive.google.com/uc?export=download&id="
        out = "{}{}".format(base_url, file_id)
    elif "dropbox.com" in url:
        if url.endswith(".png"):
            out = url + "?dl=1"
        else:
            out = url.replace("dl=0", "dl=1")
    else:
        out = url
    return out


def _fetch_file(
    url,
    file_name,
    file_kind: str,
    resume=True,
    hash_=None,
    timeout=10.0,
    progressbar=True,
    verbose=True,
    system_worker_state=None,
    check_install_kill=None,
    module_name=None,
    cur_size=0,
    total_size=0,
    outer=None,
):
    """Load requested file, downloading it if needed or requested.

    Parameters
    ----------
    url: string
        The url of file to be downloaded.
    file_name: string
        Name, along with the path, of where downloaded file will be saved.
    resume: bool, optional
        If true, try to resume partially downloaded files.
    hash_ : str | None
        The hash of the file to check. If None, no checking is
        performed.
    timeout : float
        The URL open timeout.
    verbose : bool
        Whether to print download status.
    """
    # Adapted from NISL and MNE-python:
    # https://github.com/nisl/tutorial/blob/master/nisl/datasets.py
    # https://martinos.org/mne
    from time import time
    from ...gui.consts import SYSTEM_STATE_INSTALL_KEY

    assert module_name is not None
    if hash_ is not None and (not isinstance(hash_, str) or len(hash_) != 32):
        raise ValueError(
            "Bad hash value given, should be a 32-character " "string:\n%s" % (hash_,)
        )
    temp_file_name = file_name + ".part"
    remote_file_size: Optional[int] = None
    if "dropbox.com" in url:
        # Use requests to handle cookies.
        # XXX In the future, we should probably use requests everywhere.
        # Unless we want to minimize dependencies.
        try:
            import requests
        except ModuleNotFoundError:
            raise ValueError(
                "To download Dropbox links, you need to "
                "install the `requests` module."
            )
        resp = requests.get(url, stream=True)
        chunk_size = 8192  # 2 ** 13
        if system_worker_state:
            cur_chunk = system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name][
                "cur_chunk"
            ]
            total_chunk = system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name][
                "cur_chunk"
            ]
        else:
            cur_chunk = 0
            total_chunk = 0
        t = time()
        with open(temp_file_name, "wb") as ff:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if check_install_kill and system_worker_state:
                    check_install_kill(
                        system_worker_state=system_worker_state, module_name=module_name
                    )
                if chunk:
                    ff.write(chunk)
                    if system_worker_state:
                        cur_chunk += chunk_size
                        total_chunk += chunk_size
                        if outer and time() - t > 1:
                            outer.write(
                                f"download_{file_kind}:{cur_chunk}:{total_chunk}"
                            )
    else:
        # Check file size and displaying it alongside the download url
        req = request_agent(url)
        u = urllib.request.urlopen(req, timeout=timeout)  # type: ignore
        u.close()
        # this is necessary to follow any redirects
        url = u.geturl()
        req = request_agent(url)
        u = urllib.request.urlopen(req, timeout=timeout)  # type: ignore
        try:
            remote_file_size = int(u.headers.get("Content-Length", "0").strip())
        finally:
            u.close()
            del u
        if verbose and outer:
            outer.write(f"Downloading data from {url} ({sizeof_fmt(remote_file_size)})")
        # Triage resume
        if not os.path.exists(temp_file_name):
            resume = False
        if resume:
            cur_file_size = op.getsize(temp_file_name)
        else:
            cur_file_size = 0
        # This should never happen if our functions work properly
        if cur_file_size > remote_file_size:
            raise RuntimeError(
                "Local file (%s) is larger than remote "
                "file (%s), cannot resume download"
                % (sizeof_fmt(cur_file_size), sizeof_fmt(remote_file_size))
            )
        cur_size += cur_file_size
        scheme = urllib.parse.urlparse(url).scheme  # type: ignore
        fun = _get_http if scheme in ("http", "https") else _get_ftp
        fun(
            url,
            temp_file_name,
            cur_file_size,
            remote_file_size,
            progressbar,
            file_kind,
            system_worker_state=system_worker_state,
            check_install_kill=check_install_kill,
            module_name=module_name,
            cur_size=cur_size,
            total_size=total_size,
            outer=outer,
        )
        # check md5sum
        # if hash_ is not None:
        #    if verbose and outer:
        #        outer.write("Verifying download hash.")
        #    md5 = md5sum(temp_file_name)
        #    if hash_ != md5:
        #        raise RuntimeError(
        #            "Hash mismatch for downloaded file %s, "
        #            "expected %s but got %s" % (temp_file_name, hash_, md5)
        #        )
    local_file_size = op.getsize(temp_file_name)
    if remote_file_size and local_file_size != remote_file_size:
        raise Exception(
            "Error: File size is %d and should be %d"
            "* Please wait some time and try re-downloading the file again."
            % (local_file_size, remote_file_size)
        )
    shutil.move(temp_file_name, file_name)


def _get_ftp(
    url,
    temp_file_name,
    cur_file_size,
    remote_file_size,
    progressbar,
    file_kind: str,
    system_worker_state=None,
    check_install_kill=None,
    module_name=None,
    cur_size=0,
    total_size=0,
    outer=None,
):
    """Safely (resume a) download to a file from FTP."""
    # Adapted from: https://pypi.python.org/pypi/fileDownloader.py
    # but with changes
    from time import time
    from rich.progress import Progress
    from ...gui.util import GuiOuter

    assert module_name is not None
    parsed_url = urllib.parse.urlparse(url)  # type: ignore
    file_name = os.path.basename(parsed_url.path)
    server_path = parsed_url.path.replace(file_name, "")
    unquoted_server_path = urllib.parse.unquote(server_path)  # type: ignore
    data = ftplib.FTP()
    if parsed_url.port is not None:
        data.connect(parsed_url.hostname, parsed_url.port)
    else:
        data.connect(parsed_url.hostname)
    data.login()
    if len(server_path) > 1:
        data.cwd(unquoted_server_path)
    data.sendcmd("TYPE I")
    data.sendcmd("REST " + str(cur_file_size))
    down_cmd = "RETR " + file_name
    assert remote_file_size == data.size(file_name)
    chunk_size = 262144 * 4
    if outer and progressbar:
        progress = Progress()
        task = progress.add_task(
            description=f"",
            total=remote_file_size,
            completed=cur_file_size,
        )
        progress.start()
    else:
        progress = None
        task = None
    # Callback lambda function that will be passed the downloaded data
    # chunk and will write it to file and update the progress bar
    mode = "ab" if cur_file_size > 0 else "wb"
    t = time()
    with open(temp_file_name, mode) as local_file:

        def chunk_write(chunk):
            return _chunk_write(chunk, local_file, progress, outer)

        if check_install_kill and system_worker_state:
            check_install_kill(
                system_worker_state=system_worker_state, module_name=module_name
            )
        data.retrbinary(down_cmd, chunk_write, blocksize=chunk_size)
        if progress and task is not None:
            progress.update(task, advance=chunk_size)
        cur_size += chunk_size
        if outer and isinstance(outer, GuiOuter) and time() - t > 1:
            outer.write(f"download_{file_kind}:{module_name}:{cur_size}:{total_size}")
    data.close()
    if progress:
        progress.stop()


def _get_http(
    url,
    temp_file_name,
    cur_file_size,
    remote_file_size,
    progressbar,
    file_kind: str,
    system_worker_state=None,
    check_install_kill=None,
    module_name=None,
    cur_size=0,
    total_size=0,
    outer=None,
):
    """Safely (resume a) download to a file from http(s)."""
    import requests
    from time import time
    from rich.progress import Progress
    from ...gui.util import GuiOuter

    assert module_name is not None
    session = requests.Session()
    headers = {"User-Agent": "oakvar"}
    if cur_file_size > 0:
        headers["Range"] = "bytes=%s-" % (cur_file_size,)
    try:
        r = session.get(url, headers=headers, stream=True)
    except Exception:
        if outer:
            outer.write(
                "Resuming download failed (server "
                "rejected the request). Attempting to "
                "restart downloading the entire file.",
            )
        del headers["Range"]
        r = session.get(url, headers=headers, stream=True)
    r.raise_for_status()
    total_size = int(r.headers.get("Content-Length", "0").strip())
    if cur_file_size > 0 and remote_file_size == total_size:
        if outer:
            outer.write(
                "Resuming download failed (resume file size "
                "mismatch). Attempting to restart downloading the "
                "entire file.",
                file=sys.stdout,
            )
        cur_file_size = 0
    total_size += cur_file_size
    if total_size != remote_file_size:
        raise RuntimeError("URL could not be parsed properly")
    mode = "ab" if cur_file_size > 0 else "wb"
    if outer and progressbar:
        progress = Progress()
        task = progress.add_task(
            description=f"",
            total=remote_file_size,
            completed=cur_file_size,
        )
        progress.start()
    else:
        progress = None
        task = None
    chunk_size = 262144 * 4
    t = time()
    with open(temp_file_name, mode) as local_file:
        for chunk in r.iter_content(chunk_size=chunk_size):
            t0 = time()
            if check_install_kill and system_worker_state:
                check_install_kill(
                    system_worker_state=system_worker_state, module_name=module_name
                )
            dt = time() - t0
            if dt < 0.005:
                chunk_size = chunk_size * 2
            elif dt > 0.1 and chunk_size > 8192:
                chunk_size = max(chunk_size // 2, 512)
            local_file.write(chunk)
            read_size = len(chunk)
            if progress and task is not None:
                progress.update(task, advance=read_size)
            cur_size += read_size
            if outer and isinstance(outer, GuiOuter) and time() - t > 1:
                outer.write(
                    f"download_{file_kind}:{module_name}:{cur_size}:{total_size}"
                )
    if progress:
        progress.stop()


# def md5sum(fname, block_size=1048576):  # 2 ** 20
#    """Calculate the md5sum for a file.
#
#    Parameters
#    ----------
#    fname : str
#        Filename.
#    block_size : int
#        Block size to use when reading.
#
#    Returns
#    -------
#    hash_ : str
#        The hexadecimal digest of the hash.
#    """
#    md5 = hashlib.md5()  # type: ignore
#    with open(fname, "rb") as fid:
#        while True:
#            data = fid.read(block_size)
#            if not data:
#                break
#            md5.update(data)
#    return md5.hexdigest()


def _chunk_write(chunk, local_file, progress, outer):
    """Write a chunk to file and update the progress bar."""
    local_file.write(chunk)
    if progress is not None and outer:
        progress.update(len(chunk))


def sizeof_fmt(num):
    """Turn number of bytes into human-readable str.

    Parameters
    ----------
    num : int
        The number of bytes.

    Returns
    -------
    size : str
        The size in human-readable format.
    """
    units = ["bytes", "kB", "MB", "GB", "TB", "PB"]
    decimals = [0, 0, 1, 2, 2, 2]
    if num > 1:
        exponent = min(int(log(num, 1024)), len(units) - 1)
        quotient = float(num) / 1024**exponent
        unit = units[exponent]
        num_decimals = decimals[exponent]
        format_string = "{0:.%sf} {1}" % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return "0 bytes"
    if num == 1:
        return "1 byte"


class _TempDir(str):
    """Create and auto-destroy temp dir.

    This is designed to be used with testing modules. Instances should be
    defined inside test functions. Instances defined at module level can not
    guarantee proper destruction of the temporary directory.

    When used at module level, the current use of the __del__() method for
    cleanup can fail because the rmtree function may be cleaned up before this
    object (an alternative could be using the atexit module instead).
    """

    def __new__(self):  # type: ignore # noqa: D105
        new = str.__new__(self, tempfile.mkdtemp(prefix="tmp_download_tempdir_"))
        return new

    def __init__(self):  # noqa: D102
        self._path = self.__str__()

    def __del__(self):  # noqa: D105
        shutil.rmtree(self._path, ignore_errors=True)


def request_agent(url):
    req = urllib.request.Request(  # type: ignore
        url,
        data=None,
        # Simulate a user-agent because some websites require it for this to work
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac "
            + "OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) "
            + "Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    return req

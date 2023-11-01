# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
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

from typing import Optional


def create(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    pwconfirm: bool = False,
    interactive: bool = False,
    outer=None,
) -> bool:
    """Creates an OakVar store account.

    Args:
        email (Optional[str]): Email of an OakVar store account
        pw (Optional[str]): Password of an OakVar store account
        pwconfirm (bool): Should be the same as `pw`.
        interactive (bool): If `True` and `email` or `pw` is not given, missing fields will be interactvely received with prompts.
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ....lib.store.ov.account import create

    ret = create(
        email=email, pw=pw, pwconfirm=pwconfirm, interactive=interactive, outer=outer
    )
    success: bool = ret.get("success", False)
    return success


def delete(outer=None) -> bool:
    """Deletes an OakVar store account. You should be already logged in.

    Args:
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ....lib.store.ov.account import delete

    ret = delete(outer=outer)
    return ret


def change(newpw: Optional[str] = None, outer=None) -> bool:
    """Changes the password of an OakVar store account. You should be already logged in.

    Args:
        newpw (Optional[str]): New password
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ....lib.store.ov.account import change

    ret = change(newpw=newpw, outer=outer)
    return ret


def reset(email: Optional[str], outer=None) -> bool:
    """Sends a password reset email for an OakVar store account. You should be already logged in.

    Args:
        email (Optional[str]): Email of the logged in OakVar store account
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ....lib.store.ov.account import reset

    ret = reset(email=email, outer=outer)
    return ret


def check(outer=None) -> bool:
    """Checks if you are logged in to the OakVar store.

    Args:
        outer:

    Returns:
        `True` if logged in. `False` if not.
    """
    from ....lib.store.ov.account import check_logged_in_with_token

    ret = check_logged_in_with_token(outer=outer)
    return ret

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

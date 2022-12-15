from typing import Optional

def create(email: Optional[str]=None, pw: Optional[str]=None, pwconfirm: bool=False, interactive: bool=False, outer=None):
    from ....lib.store.ov.account import create

    ret = create(email=email, pw=pw, pwconfirm=pwconfirm, interactive=interactive, outer=outer)
    ret = ret.get("success")
    return ret


def store_deleteaccount(outer=None):
    from ....lib.store.ov.account import delete

    ret = delete(outer=outer)
    return ret


def change(newpw: Optional[str]=None, outer=None):
    from ....lib.store.ov.account import change

    ret = change(newpw=newpw, outer=outer)
    return ret


def reset(email: Optional[str], outer=None):
    from ....lib.store.ov.account import reset

    ret = reset(email=email, outer=outer)
    return ret


def check(outer=None):
    from ....lib.store.ov.account import check_logged_in_with_token

    ret = check_logged_in_with_token(outer=outer)
    return ret


def login(email: Optional[str]=None, pw: Optional[str]=None, interactive: bool=False, outer=None):
    from ....lib.store.ov.account import login

    ret = login(email=email, pw=pw, interactive=interactive, outer=outer)
    return ret


def logout(outer=None):
    from ....lib.store.ov.account import logout

    ret = logout(outer=outer)
    return ret


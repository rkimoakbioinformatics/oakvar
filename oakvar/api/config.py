def user():
    from ..lib.util.admin_util import get_user_conf

    conf = get_user_conf()
    return conf


def system(key=None, value=None, type=None):
    from ..lib.system import get_sys_conf_value
    from ..lib.system import set_sys_conf_value
    from ..lib.system import get_system_conf

    if key:
        if value:
            if not type:
                type = "str"
            set_sys_conf_value(key, value, type)
            return
        else:
            ret = get_sys_conf_value(key)
            return ret
    else:
        conf = get_system_conf()
        return conf


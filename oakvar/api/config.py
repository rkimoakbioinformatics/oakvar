from typing import Optional
from typing import Union


def user() -> Optional[dict]:
    """Gets user configuration.

    Returns:
        OakVar user configuration
    """
    from ..lib.util.admin_util import get_user_conf

    conf = get_user_conf()
    return conf


def system(
    key: Optional[str] = None, value: Optional[str] = None, type: str = "str"
) -> Optional[Union[str, int, float, dict]]:
    """Gets or sets system configuration.

    Args:
        key (Optional[str]): key
        value (Optional[str]): value
        type (Optional[str]): type

    Returns:
        With no argument, system configuration is returned as a dict. With only key given, the system configuration value for the key is returned. With key, value, and type given, system configuration is updated with the value of the type for the key. If type is omitted, str is assumed.
    """
    from ..lib.system import get_sys_conf_value
    from ..lib.system import set_sys_conf_value
    from ..lib.system import get_system_conf

    if key:
        if value:
            if not type:
                type = "str"
            set_sys_conf_value(key, value, type)
            return value
        else:
            v = get_sys_conf_value(key)
            return v
    else:
        conf = get_system_conf()
        return conf

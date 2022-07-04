from ...decorators import cli_func
from ...decorators import cli_entry


@cli_entry
def cli_store_publish(args):
    return publish(args)


@cli_func
def publish(args, __name__="store publish"):
    from ...system import get_system_conf
    from ...store.oc import publish_module
    from getpass import getpass
    from ...system import consts

    if args.get("md"):
        consts.custom_modules_dir = args.get("md")
    sys_conf = get_system_conf()
    if not args.get("user"):
        if "publish_username" in sys_conf:
            args["user"] = sys_conf["publish_username"]
        else:
            args["user"] = input("Email: ")
    if not args.get("password"):
        if "publish_password" in sys_conf:
            args["password"] = sys_conf["publish_password"]
        else:
            args["password"] = getpass()
    channel = args.get("channel")
    if channel == "open-cravat":
        return publish_module(
            args.get("module"),
            args.get("user"),
            args.get("password"),
            overwrite=args.get("overwrite"),
            include_data=args.get("data"),
            quiet=args.get("quiet"),
        )
    elif channel == "oakvar":
        pass


@cli_entry
def cli_store_fetch(args):
    return fetch(args)


@cli_func
def fetch(args, __name__="store fetch"):
    from ...store.ov import fetch_ov_store_cache

    ret = fetch_ov_store_cache(args=args)
    return ret


@cli_entry
def cli_store_pack(args):
    return pack(args)


@cli_func
def pack(args, __name__="store pack"):
    from ...store.pack import pack_module

    ret = pack_module(args)
    return ret


def get_parser_fn_store():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_store = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser_fn_store.add_subparsers(title="Commands")
    add_parser_store_account(subparsers)
    add_parser_fn_store_publish(subparsers)
    add_parser_fn_store_fetch(subparsers)
    add_parser_fn_store_pack(subparsers)
    add_parser_fn_store_oc(subparsers)
    return parser_fn_store


def add_parser_store_account(subparsers):
    from ..store.account import add_parser_fn_store_account

    add_parser_fn_store_account(subparsers)


def add_parser_fn_store_publish(subparsers):
    # publish
    parser_cli_store_publish = subparsers.add_parser(
        "publish", help="publishes a module."
    )
    parser_cli_store_publish.add_argument("module", help="module to publish")
    data_group = parser_cli_store_publish.add_mutually_exclusive_group(required=True)
    data_group.add_argument(
        "--include-data",
        action="store_true",
        default=False,
        help="include data",
    )
    parser_cli_store_publish.add_argument(
        "--email", default=None, help="email of your account"
    )
    parser_cli_store_publish.add_argument(
        "--password",
        default=None,
        help="password of your account",
    )
    parser_cli_store_publish.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="overwrites the same version module",
    )
    parser_cli_store_publish.add_argument(
        "--md", default=None, help="custom modules root directory"
    )
    parser_cli_store_publish.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_publish.add_argument(
        "--channel",
        default="oakvar",
        choices=["oakvar", "open-cravat"],
        help="channel to publish. oakvar or open-cravat.",
    )
    parser_cli_store_publish.add_argument(
        "--code-url",
        help="url of a code pack (made with `ov store pack`). Needed only for the OakVar Store",
    )
    parser_cli_store_publish.add_argument(
        "--data-url",
        help="url of a data pack (made with `ov store pack`). Needed only for the OakVar Store",
    )
    parser_cli_store_publish.set_defaults(func=cli_store_publish)
    parser_cli_store_publish.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_publish.r_examples = [  # type: ignore
        '# Publish "customannot" module to the store',
        '#roakvar::store.publish(module="customannot", user="user1", password="password")',
    ]


def add_parser_fn_store_fetch(subparsers):
    # fetch
    parser_cli_store_fetch = subparsers.add_parser("fetch", help="fetch store cache")
    parser_cli_store_fetch.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_fetch.add_argument(
        "--email", default=None, help="email of OakVar store account"
    )
    parser_cli_store_fetch.add_argument(
        "--pw", default=None, help="password of OakVar store account"
    )
    parser_cli_store_fetch.set_defaults(func=cli_store_fetch)
    parser_cli_store_fetch.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_fetch.r_examples = [  # type: ignore
        "# Fetch the store information",
        "#roakvar::store.fetch()",
    ]


def add_parser_fn_store_pack(subparsers):
    # pack
    parser_cli_store_pack = subparsers.add_parser(
        "pack", help="pack a module to register at OakVar store"
    )
    parser_cli_store_pack.add_argument(
        dest="module",
        default=None,
        help="Name of or path to the module to pack",
    )
    parser_cli_store_pack.add_argument(
        "-d",
        "--outdir",
        default=".",
        help="Directory to make code and data zip files in",
    )
    parser_cli_store_pack.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_pack.set_defaults(func=cli_store_pack)
    parser_cli_store_pack.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_pack.r_examples = [  # type: ignore
        '# Pack a module "mymodule" into one zip file for its code and another zip file for its data.',
        '#roakvar::store.pack(module="mymodule")',
    ]


def add_parser_fn_store_oc(subparsers):
    from ..store.oc import add_parser_fn_store_oc

    add_parser_fn_store_oc(subparsers)

import argparse
from . import cravat_admin, cravat_util
from .cravat_class import parser as oakvar_cmd_parser
from .cravat_test import parser as oakvar_test_parser
from .cravat_web import parser as oakvar_web_parser
from .cravat_report import parser as oakvar_report_parser
import sys

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("@ error:", message)
        self.print_help(sys.stderr)

p_entry = ArgumentParser(
    description="OakVar. Genomic variant analysis platform. https://github.com/rkimoakbioinformatics/oakvar"
)
sp_entry = p_entry.add_subparsers(title="Commands")

# run
p_run = sp_entry.add_parser(
    "run",
    parents=[oakvar_cmd_parser],
    add_help=False,
    description="Run a job",
    help="Run a job",
    epilog="inputs should be the first argument",
)

# report
p_report = sp_entry.add_parser(
    "report",
    parents=[oakvar_report_parser],
    add_help=False,
    help="Generate a report from a job",
    epilog="dbpath must be the first argument",
)

# gui
p_gui = sp_entry.add_parser(
    "gui", parents=[oakvar_web_parser], add_help=False, help="Start the GUI"
)

# module
p_module = sp_entry.add_parser(
    "module", description="Change installed modules", help="Change installed modules"
)
sp_module = p_module.add_subparsers(title="Commands")
p_module_ls = sp_module.add_parser(
    "ls", parents=[cravat_admin.parser_ls], add_help=False, help="List modules"
)
p_module_install = sp_module.add_parser(
    "install",
    description="Install modules",
    parents=[cravat_admin.parser_install],
    add_help=False,
    help="Install modules",
)
p_module_uninstall = sp_module.add_parser(
    "uninstall",
    parents=[cravat_admin.parser_uninstall],
    add_help=False,
    help="Uninstall modules",
)
p_module_update = sp_module.add_parser(
    "update",
    parents=[cravat_admin.parser_update],
    add_help=False,
    help="Update modules",
)
p_module_info = sp_module.add_parser(
    "info", parents=[cravat_admin.parser_info], add_help=False, help="Module details"
)
p_module_installbase = sp_module.add_parser(
    "installbase",
    parents=[cravat_admin.parser_install_base],
    add_help=False,
    help="Install base modules",
)


# config
p_config = sp_entry.add_parser(
    "config",
    description="View and change configuration settings",
    help="View and change configuration settings",
)
sp_config = p_config.add_subparsers(title="Commands")
p_config_md = sp_config.add_parser(
    "md",
    parents=[cravat_admin.parser_md],
    add_help=False,
    help="Change modules directory",
)
p_config_system = sp_config.add_parser(
    "system",
    parents=[cravat_admin.parser_show_system_conf],
    add_help=False,
    help="Show system config",
)
p_config_cravat = sp_config.add_parser(
    "cravat",
    parents=[cravat_admin.parser_show_cravat_conf],
    add_help=False,
    help="Show cravat config",
)

# new
p_new = sp_entry.add_parser(
    "new", description="Create new modules", help="Create new modules"
)
sp_new = p_new.add_subparsers(title="Commands")
p_new_exampleinput = sp_new.add_parser(
    "exampleinput",
    parents=[cravat_admin.parser_make_example_input],
    add_help=False,
    help="Make example input file",
)
p_new_annotator = sp_new.add_parser(
    "annotator",
    parents=[cravat_admin.parser_new_annotator],
    add_help=False,
    help="Create new annotator",
)

# store
p_store = sp_entry.add_parser(
    "store",
    description="Publish modules to the store",
    help="Publish modules to the store",
)
sp_store = p_store.add_subparsers(title="Commands")
p_store_publish = sp_store.add_parser(
    "publish",
    parents=[cravat_admin.parser_publish],
    add_help=False,
    help="Publish a module",
)
p_store_newaccount = sp_store.add_parser(
    "newaccount",
    parents=[cravat_admin.parser_create_account],
    add_help=False,
    help="Create a publish account",
)
p_store_changepw = sp_store.add_parser(
    "changepw",
    parents=[cravat_admin.parser_change_password],
    add_help=False,
    help="Change the password of a publish account",
)
p_store_resetpw = sp_store.add_parser(
    "resetpw",
    parents=[cravat_admin.parser_reset_pw],
    add_help=False,
    help="Request reset the password of a publish account",
)
p_store_verifyemail = sp_store.add_parser(
    "verifyemail",
    parents=[cravat_admin.parser_verify_email],
    add_help=False,
    help="Request email verification for a publish account",
)
p_store_checklogin = sp_store.add_parser(
    "checklogin",
    parents=[cravat_admin.parser_check_login],
    add_help=False,
    help="Check the login credentials of a publish account",
)

# util
p_util = sp_entry.add_parser("util", description="Utilities", help="Utilities")
sp_util = p_util.add_subparsers(title="Commands")
p_util_test = sp_util.add_parser(
    "test", parents=[oakvar_test_parser], add_help=False, help="Test installed modules"
)
p_util_updateresult = sp_util.add_parser(
    "updateresult",
    parents=[cravat_util.parser_migrate_result],
    add_help=False,
    help="Update old result database to newer format",
)
p_util_sendgui = sp_util.add_parser(
    "sendgui",
    parents=[cravat_util.parser_result2gui],
    add_help=False,
    help="Copy a command line job into the GUI submission list",
)
p_util_mergesqlite = sp_util.add_parser(
    "mergesqlite",
    parents=[cravat_util.parser_mergesqlite],
    add_help=False,
    help="Merge SQLite result files",
)
p_util_filtersqlite = sp_util.add_parser(
    "filtersqlite",
    parents=[cravat_util.parser_filtersqlite],
    add_help=False,
    help="Filter SQLite result files",
)
p_util_showsqliteinfo = sp_util.add_parser(
    "showsqliteinfo",
    parents=[cravat_util.parser_showsqliteinfo],
    add_help=False,
    help="Show SQLite result file information",
)

# version
p_version = sp_entry.add_parser(
    "version",
    parents=[cravat_admin.parser_show_version],
    add_help=False,
    help="Show version",
)

# feedback
p_feedback = sp_entry.add_parser(
    name="feedback",
    parents=[cravat_admin.parser_report_issue],
    add_help=False,
    help="Send feedback to the developers",
)


def main():
    try:
        args = p_entry.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            p_entry.parse_args(sys.argv[1:] + ["--help"])
    except SystemExit:
        return


if __name__ == "__main__":
    main()

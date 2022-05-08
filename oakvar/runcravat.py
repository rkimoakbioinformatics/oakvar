#!/usr/bin/env python3
from oakvar.cravat_class import Cravat, cravat_cmd_parser
from oakvar.admin_util import ready_resolution_console


def main():
    ready_resolution_console()
    cmd_args = cravat_cmd_parser.parse_args()
    cmd_args.func(cmd_args)


if __name__ == "__main__":
    main()

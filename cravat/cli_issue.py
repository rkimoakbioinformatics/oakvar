def fn_issue(args):
    from .admin_util import report_issue

    report_issue()


def get_parser_fn_issue():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    # opens issue report
    parser_fn_feedback = (
        ArgumentParser()
    )  # "feedback", help="opens a browser window to report issues")
    parser_fn_feedback.set_defaults(func=fn_issue)
    return parser_fn_feedback

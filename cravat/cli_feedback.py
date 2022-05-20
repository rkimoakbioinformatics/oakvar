def fn_feedback(args):
    from .admin_util import report_issue

    report_issue()


def get_parser_fn_feedback():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    # opens issue report
    parser_fn_feedback = (
        ArgumentParser()
    )  # "feedback", help="opens a browser window to report issues")
    parser_fn_feedback.set_defaults(func=fn_feedback)
    return parser_fn_feedback

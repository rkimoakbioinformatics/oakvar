def fn_issue(__args__):
    from .admin_util import report_issue
    return report_issue()


def get_parser_fn_issue():
    from argparse import ArgumentParser
    # opens issue report
    parser_fn_feedback = (
        ArgumentParser()
    )  # "feedback", help="opens a browser window to report issues")
    parser_fn_feedback.add_argument("--quiet",
                                    default=True,
                                    help="Run quietly")
    parser_fn_feedback.set_defaults(func=fn_issue)
    return parser_fn_feedback

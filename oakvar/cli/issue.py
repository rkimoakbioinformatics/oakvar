from . import cli_entry
from . import cli_func


@cli_entry
@cli_func
def issue(__args__, __name__="issue"):
    from ..api import report_issue

    return report_issue()


def get_parser_fn_issue():
    from argparse import ArgumentParser

    # opens issue report
    parser_fn_feedback = (
        ArgumentParser()
    )  # "feedback", help="opens a browser window to report issues")
    parser_fn_feedback.set_defaults(func=issue)
    return parser_fn_feedback

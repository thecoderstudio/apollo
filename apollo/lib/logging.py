import logging
from copy import copy

import click
from uvicorn.logging import ColourizedFormatter

audit_logger = logging.getLogger('audit')

GRANTED = 'granted'
DENIED = 'denied'


class AuditFormatter(ColourizedFormatter):
    access_colors = {
        GRANTED: 'green',
        DENIED: 'red'
    }

    def format_access(self, access):
        return click.style(access.upper(), fg=self.access_colors[access],
                           bold=False)

    def format_permission_log(self, record_msg):
        if GRANTED in record_msg:
            record_msg = record_msg.replace(GRANTED,
                                            self.format_access(GRANTED))
        elif DENIED in record_msg:
            record_msg = record_msg.replace(DENIED,
                                            self.format_access(DENIED))

        return record_msg

    def formatMessage(self, record):
        record_copy = copy(record)

        styled_message = click.style(record_copy.msg, bold=True)

        if 'Permission' in record_copy.msg:
            styled_message = self.format_permission_log(styled_message)

        record_copy.__dict__['color_message'] = styled_message

        return super().formatMessage(record_copy)

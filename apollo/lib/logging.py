from copy import copy

import click
from uvicorn.logging import ColourizedFormatter


class AuditFormatter(ColourizedFormatter):
    access_colors = {
        'granted': 'green',
        'denied': 'red'
    }

    def format_access(self, access):
        return click.style(access.upper(), fg=self.access_colors[access],
                           bold=False)

    def format_permission_log(self, record_msg):
        if 'granted' in record_msg:
            record_msg = record_msg.replace('granted',
                                            self.format_access('granted'))
        elif 'denied' in record_msg:
            record_msg = record_msg.replace('denied',
                                            self.format_access('denied'))

        return record_msg

    def formatMessage(self, record):
        record_copy = copy(record)

        styled_message = click.style(record_copy.msg, bold=True)

        if 'Permission' in record_copy.msg:
            styled_message = self.format_permission_log(styled_message)

        record_copy.__dict__['color_message'] = styled_message

        return super().formatMessage(record_copy)

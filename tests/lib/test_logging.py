import click
import pytest
from logging import LogRecord, INFO

from apollo.lib.logging import AuditFormatter

GRANTED = click.style('GRANTED', fg='green', bold=False)
DENIED = click.style('DENIED', fg='red', bold=False)

FAKE_GRANT = "Permission 'fake' granted"
FAKE_DENIED = "Permission 'fake' denied"
LOREM = "Lorem ipsum"

FAKE_GRANT_STYLED = click.style(FAKE_GRANT, bold=True).replace(
    'granted', GRANTED)
FAKE_DENIED_STYLED = click.style(FAKE_DENIED, bold=True).replace(
    'denied', DENIED)
LOREM_STYLED = click.style(LOREM, bold=True)


@pytest.mark.parametrize("access,expected", (
    ('granted', GRANTED),
    ('denied', DENIED)
))
def test_audit_formatter_format_access(access, expected):
    assert AuditFormatter().format_access(access) == expected


@pytest.mark.parametrize("msg,expected", (
    (FAKE_GRANT, FAKE_GRANT.replace('granted', GRANTED)),
    (FAKE_DENIED, FAKE_DENIED.replace('denied', DENIED)),
    (LOREM, LOREM)
))
def test_audit_formatter_format_permission_log(msg, expected):
    assert AuditFormatter().format_permission_log(msg) == expected


@pytest.mark.parametrize("msg,expected", (
    (FAKE_GRANT, FAKE_GRANT_STYLED),
    (FAKE_DENIED, FAKE_DENIED_STYLED),
    (LOREM, LOREM_STYLED)
))
def test_audit_formatter_format_message(msg, expected):
    record = LogRecord(
        name='fake',
        level=INFO,
        pathname='/fake.py',
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None
    )
    record.__dict__['message'] = record.msg
    assert AuditFormatter(use_colors=True).formatMessage(record) == expected

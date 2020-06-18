import click
import pytest

from apollo.lib.logging import AuditFormatter


@pytest.mark.parametrize("access,expected", (
    ('granted', click.style('GRANTED', fg='green', bold=False)),
    ('denied', click.style('DENIED', fg='red', bold=False))
))
def test_audit_formatter_format_access(access, expected):
    assert AuditFormatter().format_access(access) == expected


def test_audit_formatter_format_permission_log():
    pass


def test_audit_formatter_format_message():
    pass

import datetime

from apollo.models.oauth import OAuthAccessToken


def test_oauth_access_token_expired():
    expired_token = OAuthAccessToken(
        expiry_date=datetime.datetime.now(datetime.timezone.utc)
    )
    unexpired_token = OAuthAccessToken(
        expiry_date=datetime.datetime.now(datetime.timezone.utc) +
        datetime.timedelta(hours=1)
    )

    assert expired_token.expired
    assert not unexpired_token.expired

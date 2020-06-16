from apollo.lib.settings import settings


def get_origins():
    web_domain = settings['Web']['domain']
    web_port = settings['Web']['port']
    return (
        f"http://{web_domain}:{web_port}",
        f"https://{web_domain}:{web_port}"
    )

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Authenticated

router = SecureRouter([
    (Allow, Authenticated, 'agent.action')
])

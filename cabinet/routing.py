from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import simulation.routing as smr

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            smr.websocket_urlpatterns
        )
    ),
})

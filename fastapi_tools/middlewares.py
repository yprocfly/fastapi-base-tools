from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send, Message


class SimpleBaseMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.default_send = None    # type Send
        self.initial_message = {}   # type Message

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        self.default_send = send
        request = Request(scope, receive=receive)
        response = await self.response_rewrite(request)
        if response and isinstance(response, Response):
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, self.send_rewrite)

    async def response_rewrite(self, request: Request) -> [Response, None]:
        """重写response"""
        return None

    async def send_rewrite(self, message: Message) -> None:
        """重写send方法【不重写则默认使用原来的】"""
        await self.default_send(message)

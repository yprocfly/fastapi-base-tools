from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send, Message


class SimpleBaseMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.default_send = None    # type Send

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        self.default_send = send
        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, self.send)
        await self.after_request(request)

    async def before_request(self, request: Request) -> [Response, None]:
        """如果需要修改请求信息，可直接重写此方法"""
        return self.app

    async def after_request(self, request: Request):
        """请求后的处理【记录请求耗时等，注意这里没办法对响应结果进行处理】"""
        return None

    async def send(self, message: Message) -> None:
        """重写send方法【不重写则默认使用原来的】"""
        await self.default_send(message)

    async def update_request_header(self, request, key, value):
        """更新请求头"""
        key, value = str(key).encode(), str(value).encode()
        for index, item in enumerate(request.scope['headers']):
            if item[0] == key:
                request.scope['headers'][index] = (key, value)
                return

        request.scope['headers'].append((key, value))


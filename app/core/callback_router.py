import re


class CallbackRouter:

    def __init__(
            self: 'CallbackRouter'
    ) -> None:

        self.routes = []

    def register(
        self: 'CallbackRouter',
        pattern: str,
        handler: callable
    ) -> None:

        compiled = re.compile(pattern)

        self.routes.append(
            (compiled, handler)
        )

    async def dispatch(
        self: 'CallbackRouter',
        callback_data: str,
        *args: tuple,
        **kwargs: dict
    ) -> any:

        for regex, handler in self.routes:

            match = regex.match(callback_data)

            if match:

                return await handler(
                    *args,
                    callback_data=callback_data,
                    match=match,
                    **kwargs
                )

        return None
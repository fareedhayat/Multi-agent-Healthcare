import asyncio
import logging
import functools
from autogen_agentchat import EVENT_LOGGER_NAME

def label_tool(label: str):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                logging.getLogger(EVENT_LOGGER_NAME).info(f"[Label] {label}")
                return await func(*args, **kwargs)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logging.getLogger(EVENT_LOGGER_NAME).info(f"[Label] {label}")
                return func(*args, **kwargs)
        return wrapper
    return decorator
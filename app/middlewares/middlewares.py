import json

import pydantic
from aiohttp import web
from loguru import logger

from app.db.config import AsyncLocalSession
from app.middlewares import exceptions


@web.middleware
async def bad_responses(request, handler):
    request["session"] = AsyncLocalSession()
    try:
        await request["session"].begin()
        response = await handler(request)
        await request["session"].commit()
        return response

    except web.HTTPException as e:
        logger.error(e)
        await request["session"].rollback()
        if e.status == 404:
            return web.json_response({"details": "Not Found"}, status=404)
        elif e.status == 405:
            return web.json_response({"details": "Method Not Allowed"}, status=405)

    except pydantic.ValidationError as e:
        logger.info(e)
        await request["session"].rollback()
        return web.json_response({'details': json.loads(e.json())}, status=422)

    except exceptions.UserNotFound as e:
        logger.info(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=404)

    except exceptions.UserAlreadyExists as e:
        logger.info(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=403)

    except exceptions.BalanceNotFound as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=404)

    except exceptions.TransactionNotFound as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=404)

    except exceptions.InsufficientFunds as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=402)

    except exceptions.UnknownTransactionType as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=422)

    except exceptions.TransactionAlreadyExists as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": str(e)}, status=200)

    except Exception as e:
        logger.error(e)
        await request["session"].rollback()
        return web.json_response({"details": "Internal error"}, status=500)

    finally:
        await request["session"].close()

import asyncio
import json

from pyopenuv import Client
from pyopenuv.errors import OpenUvError


async def main():
    client = Client(
        "a42986dfc544f52e8413a96cbcf84041", "34.0671637", "-84.2115892", altitude="1158"
    )

    try:
        # Get current UV info:
        result = await client.uv_index()

        if result is not None:
            content = result['result']
            # print(content)
            if content is not None:
                  print(content['uv'])

        # Get forecasted UV info:
        # print(await client.uv_forecast())

        # Get UV protection window:
        # print(await client.uv_protection_window())
    except OpenUvError as err:
        print(f"There was an error: {err}")


asyncio.run(main())

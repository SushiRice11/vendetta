from aiohttp import ClientTimeout

async def name_to_uuid(bot, name):
    url = bot.config["linking"]["mcn_endpoint"].format(name)
    async with bot.session.get(url, timeout=ClientTimeout(5)) as resp:
        data = await resp.json()
        return data["id"]

async def uuid_to_name(bot, uuid):
    url = bot.config["linking"]["mcu_endpoint"].format(uuid)
    async with bot.session.get(url, timeout=ClientTimeout(5)) as resp:
        data = await resp.json()
        return data[-1]["name"]

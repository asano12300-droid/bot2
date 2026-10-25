def groups(bot, name: str, description: str):
    group = bot.create_group(name=name, description=description)
    return group
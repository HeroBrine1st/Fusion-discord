import discord


class Bot(discord.Client):
    def get_embed(self, color=0x00FF00, title="Эмбед", **kwargs) -> discord.Embed:
        embed = discord.Embed(color=color, **kwargs)
        embed.set_author(name=title, icon_url=self.user.avatar_url)
        return embed

    def get_error_embed(self, text, title="Ошибка"):
        embed = self.get_embed(color=0xFF4C4C, title=title, description=text)
        return embed

import discord


class Bot(discord.Client):
    def get_special_embed(self, color=0xFFFFFF, title="Эмбед") -> discord.Embed:
        embed = discord.Embed(color=color)
        embed.set_author(name=title, icon_url=self.user.avatar_url)

        return embed

    get_embed = get_special_embed

    async def send_info_embed(self, channel: discord.TextChannel, text: str = None, title: str = "Инфо"):
        role = channel.guild.me.top_role
        color = 0xb63a6b

        if role:
            color = role.color.value

        embed = self.get_special_embed(title=title, color=color)
        embed.description = text

        await channel.send(embed=embed)

    def send_error_embed(self, channel: discord.TextChannel, text: str = None, title: str = "Ошибка"):
        embed = self.get_special_embed(0xFF4C4C, title=title)
        embed.description = text

        return channel.send(embed=embed)

    def send_ok_embed(self, channel: discord.TextChannel, text: str = None, title: str = "ОК"):
        embed = self.get_special_embed(0x6AAF6A, title=title)
        embed.description = text

        return channel.send(embed=embed)

    def get_info_embed(self, guild: discord.Guild, text: str = None, title: str = "Инфо"):
        role = guild.me.top_role
        color = 0xb63a6b

        if role:
            color = role.color.value

        embed = self.get_special_embed(title=title, color=color)
        embed.description = text

        return embed

    def get_error_embed(self, text: str = None, title: str = "Ошибка"):
        embed = self.get_special_embed(0xFF4C4C, title=title)
        embed.description = text

        return embed

    def get_ok_embed(self, text: str = None, title: str = "ОК"):
        embed = self.get_special_embed(0x6AAF6A, title=title)
        embed.description = text

        return embed

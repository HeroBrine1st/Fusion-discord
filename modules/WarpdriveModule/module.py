import asyncio

import discord
from core import ModuleBase, CommandResult, Command, Bot, DotDict, EventListener, services, CommandException, \
    FuturePermission


class PingCommand(Command):
    name = "wdping"
    description = "Сканирование радаром WarpDrive"
    arguments = "--service=default"
    future_permissions = {FuturePermission.GROUP}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        client_name = keys.service or "default"
        try:
            client = services[client_name]
        except KeyError:
            raise CommandException("Такого сервиса не существует.")
        OC = client.get_interface()
        radius = int(len(args) > 0 and args[0] or 200)
        if radius < 1 or radius > 10000:
            raise CommandException("Радиус должен быть значением между 1 и 10000")
        radar = OC.component.warpdriveRadar
        # ДА ИДИ НАХУЙ НЕ Я ВЫБИРАЮ ЧТО МНЕ ВЕРНУТ
        # noinspection PyUnusedLocal
        [energy, max_energy] = await radar.energy()
        [required_energy] = await radar.getEnergyRequired(radius)
        if energy < required_energy:
            raise CommandException("%s/%s" % (energy, required_energy), title="Недостаточно энергии")
        [scan_duration] = await radar.getScanDuration(radius)
        await radar.radius(radius)
        await radar.start()
        embed = self.bot.get_info_embed(title="Команда выполняется..",
                                        description="Подождите %s секунд" % scan_duration)
        msg: discord.Message = await message.channel.send(embed=embed)
        await asyncio.sleep(scan_duration + 0.5)
        results = await radar.getResults()
        embed = self.bot.get_ok_embed(title="Результаты сканирования")
        if results:
            groups = {}
            for result in results:
                if result[5] == 0 and result[1] == "default":
                    continue
                if result[1] in groups:
                    groups[result[1]].append(result)
                else:
                    groups[result[1]] = [result]
            for group_name in groups:
                group = groups[group_name]
                desc = ""
                for elem in group:
                    desc = desc + "%s %s %s с массой %s \n" % tuple(elem[2:])
                embed.add_field(name="%s" % group_name, value=desc)
        if not embed.fields:
            embed.description = "Нет результатов"
        await msg.edit(embed=embed)
        return CommandResult.success


class Module(ModuleBase):
    name = "WarpdriveModule"
    description = "Module WarpdriveModule"

    @EventListener
    def on_load(self, bot: Bot):
        self.register(PingCommand(bot))

    @EventListener
    async def run(self, bot: Bot):
        pass

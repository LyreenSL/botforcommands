from aiogram.types import BotCommand


async def set_commands(bot):
    commands = [
        BotCommand(command='/start', description='Описание'),
        BotCommand(command='/help', description='Описание'),

        BotCommand(command='/cancel', description='Прервать действие'),

        BotCommand(command='/trigger_add', description='Добавить слово-триггер'),
        BotCommand(command='/trigger_remove', description='Удалить слово-триггер'),
        BotCommand(command='/trigger_show', description='Показать все слова с ответами'),

        BotCommand(command='/action_add', description='Добавить действие'),
        BotCommand(command='/action_remove', description='Удалить действие'),
        BotCommand(command='/action_show', description='Показать все действия'),

        BotCommand(command='/welcome_add', description='Добавить приветственное сообщение'),
        BotCommand(command='/welcome_remove', description='Удалить приветственное сообщение'),
        BotCommand(command='/welcome_show', description='Показать приветственное сообщение'),

        BotCommand(command='/members_rights_off', description='Запретить редактирование для не админов'),
        BotCommand(command='/members_rights_on', description='Разрешить редактирование для не админов'),

        BotCommand(command='/data_get', description='Получить json-файл со всеми настройками для данного чата'),
        BotCommand(command='/data_set', description='Задать настройки для данного чата из json-файла'),
    ]
    await bot.set_my_commands(commands)


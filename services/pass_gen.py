from pathlib import Path
from secrets import choice
from string import ascii_letters, digits, punctuation


async def generate_password(symbols_count: int = 8) -> str:
    """
    Generates password with symbols_count symbols
    Создаёт пароль из symbols_count символов.
    :param symbols_count: количество символов, из которых будет состоять пароль
    :return: password
    """

    alphabet = *tuple(ascii_letters), *tuple(digits), *tuple(
        punctuation.replace("\\", "").replace("/", ""))
    return ''.join(choice(alphabet) for i in range(symbols_count))


async def generate_password_xkcd(words_count: int = 3, words: list | None = None) -> str:
    """
    Generates password with words_conut words
    Создаёт пароль из words_count слов.
    :param words_count: количество слов, из которых будет состоять пароль при наличии словаря в системе
    :param words: свой словарь-список слов для генерации
    :return: password
    """

    if words is None or len(words) == 0:

        if Path("/usr/share/dict/words").exists():
            with open("/usr/share/dict/words") as f:
                words = [word.strip() for word in f]
        else:
            raise FileNotFoundError("В системе не найден файл /usr/share/dict/words, "
                                    "который должен содержать список слов.")

    alphabet = *tuple(digits), *tuple(punctuation.replace("\\", "").replace("/", ""))

    password = f"{choice(words)}"
    while words_count - 1:
        words_count -= 1
        password = f"{password}{choice(alphabet)}{choice(words)}"

    return password


if __name__ == '__main__':
    from asyncio import gather, run


    async def main():
        return await gather(generate_password(), generate_password_xkcd(), return_exceptions=True)


    print(run(main()))

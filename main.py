import re
import requests
import argparse
from typing import Any

from langdetect import detect, LangDetectException


def fetch_tkk() -> tuple[int, int]:
    """
    Получает значения TKK с сайта Google Translate

    Returns:
        tuple[int, int]: Кортеж из двух целых чисел TKK
    """
    url = "https://translate.googleapis.com/translate_a/element.js"
    response = requests.get(url)
    response.raise_for_status()
    element_js = response.text

    tkk_pattern = re.compile(r"c\._ctkk='(\d+)\.(\d+)'")
    matcher = tkk_pattern.search(element_js)

    if not matcher:
        raise ValueError("TKK не найден.")

    value1 = int(matcher.group(1))
    value2 = int(matcher.group(2))

    return value1, value2


def calculate(num: int, operations: str) -> int:
    """
    Выполняет вычисления над числом 'num' по строке операций 'operations'

    Args:
        num (int): Начальное целое число
        operations (str): Строка, содержащая операции

    Returns:
        int: Результат вычисления
    """
    result = num
    for i in range(0, len(operations) - 2, 3):
        op_char = operations[i]
        shift_op = operations[i + 1]
        shift_amount_char = operations[i + 2]

        if 'a' <= shift_amount_char:
            shift_amount = ord(shift_amount_char) - 87
        else:
            shift_amount = int(shift_amount_char)

        if shift_op == '+':
            shifted = result >> shift_amount
        else:
            shifted = result << shift_amount

        if op_char == '+':
            result = (result + shifted) & 0xFFFFFFFF
        else:
            result = result ^ shifted

    return result


def tk(text: str, tkk: tuple[int, int]) -> str:
    """
    Вычисляет значение 'tk' для текста на основе TKK

    Args:
        text (str): Текст для перевода
        tkk (tuple[int, int]): Кортеж с двумя целыми числами TKK

    Returns:
        str: Значение 'tk'
    """
    bytes_array = []
    i = 0
    while i < len(text):
        char_code = ord(text[i])
        if char_code < 128:
            bytes_array.append(char_code)
        else:
            if char_code < 2048:
                bytes_array.append((char_code >> 6) | 192)
            else:
                if 0xD800 <= char_code <= 0xDBFF and i + 1 < len(text):
                    next_char_code = ord(text[i + 1])
                    if 0xDC00 <= next_char_code <= 0xDFFF:
                        # Обработка суррогатной пары
                        char_code = 0x10000 + ((char_code - 0xD800) << 10) + (next_char_code - 0xDC00)
                        bytes_array.append((char_code >> 18) | 240)
                        bytes_array.append(((char_code >> 12) & 63) | 128)
                        i += 1  # Пропустить следующий символ
                    else:
                        bytes_array.append((char_code >> 12) | 224)
                else:
                    bytes_array.append((char_code >> 12) | 224)
                bytes_array.append(((char_code >> 6) & 63) | 128)
            bytes_array.append((char_code & 63) | 128)
        i += 1

    first_int, second_int = tkk
    result = first_int
    for value in bytes_array:
        result += value
        result = calculate(result, "+-a^+6")
    result = calculate(result, "+-3^+b+-f")
    result ^= second_int
    if result < 0:
        result = (result & 0x7FFFFFFF) + 0x80000000
    result %= 1000000
    return f"{result}.{result ^ first_int}"


def translate_text(text: str, tk_value: str, sl: str, tl: str) -> dict[str, Any]:
    """
    Отправляет запрос в Google Translate для перевода текста

    Args:
        text (str): Текст для перевода
        tk_value (str): Значение 'tk' для запроса
        sl (str): Код исходного языка
        tl (str): Код целевого языка

    Returns:
        dict[str, Any]: Ответ от API в формате JSON
    """
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": sl,
        "tl": tl,
        "dt": ["t", "bd", "rm", "qca", "ex"],
        "dj": 1,
        "ie": "UTF-8",
        "oe": "UTF-8",
        "hl": "en",
        "tk": tk_value
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.102 Safari/537.36"
        ),
        "Referer": "https://translate.google.com/",
    }
    data = {"q": text}

    response = requests.post(url, params=params, headers=headers, data=data)
    response.raise_for_status()
    return response.json()


def main():
    """
    Разбор аргументов и выполнение перевода
    """
    parser = argparse.ArgumentParser(
        description="Перевод текста с использованием Google Translate API"
    )
    parser.add_argument('-t', '--text', required=True, help="Текст для перевода")

    parser.add_argument(
        '-a', '--auto', action='store_true', help="Автоматически определить исходный язык"
    )
    parser.add_argument(
        '-sl', '--source-language', default="en", help="Исходный язык (по умолчанию: en)"
    )
    parser.add_argument(
        '-tl', '--target-language', default="ru", help="Целевой язык (по умолчанию: ru)"
    )

    args = parser.parse_args()

    if args.auto or not args.source_language:
        try:
            source_language = detect(args.text)
        except LangDetectException as e:
            print(f"Не удалось определить исходный язык: {e}")
            return
    else:
        source_language = args.source_language

    try:
        tkk = fetch_tkk()
        tk_value = tk(args.text, tkk)
        translation = translate_text(
            args.text, tk_value, source_language, args.target_language
        )
        print(translation['sentences'][0]['trans'])
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()

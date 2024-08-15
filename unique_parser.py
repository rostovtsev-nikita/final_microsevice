import requests
from bs4 import BeautifulSoup
import Levenshtein
import json


def fetch_site_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяем успешность запроса
        return response.text, response.status_code
    except requests.RequestException as e:
        return str(e), getattr(e.response, 'status_code', None)
# Выполняет HTTP-запрос к указанному URL и возвращает содержимое страницы
# или ошибку с соответствующим кодом состояния HTTP.


def clean_text(text):
    # Убираем пробелы и табуляции, приводим к нижнему регистру
    return ''.join(text.split()).lower()
# Удаляет пробелы и табуляции из текста и приводит его к нижнему регистру для унификации текста.

def find_phrase(content, phrase):
    cleaned_content = clean_text(content)
    cleaned_phrase = clean_text(phrase)

    min_distance = len(cleaned_phrase)  # Инициализируем максимальным расстоянием
    phrase_found = False

    # Поиск фразы с учетом допустимого расстояния Левенштейна (не более 2)
    for i in range(len(cleaned_content) - len(cleaned_phrase) + 1):
        sub_string = cleaned_content[i:i + len(cleaned_phrase)]
        distance = Levenshtein.distance(sub_string, cleaned_phrase)
        if distance <= 2:
            phrase_found = True
            min_distance = min(min_distance, distance)

    return phrase_found, min_distance
# Ищет фразу в тексте страницы с учетом допустимого расстояния Левенштейна (не более 2).
# Возвращает факт наличия фразы и минимальное расстояние Левенштейна.

def analyze_website(url, phrase):
    content, status_code = fetch_site_content(url)

    if status_code != 200:
        return {
            "error": "Ошибка извлечения веб-страницы",
            "http_code": status_code
        }

    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)

    phrase_found, distance = find_phrase(text, phrase)

    return {
        "phrase_found": phrase_found,
        "levenshtein_distance": distance
    }
# Получает содержимое сайта.
# Парсит текст страницы с помощью BeautifulSoup.
# Проверяет наличие фразы и рассчитывает расстояние Левенштейна.

def save_result_to_json(result, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)


def get_input_from_user():
    url = input("Введите URL сайта: ")
    phrase = input("Введите фразу для поиска: ")
    return url, phrase


if __name__ == "__main__":
    # Определение режима работы
    mode = input("Выберите режим работы (1 - использовать данные из программы, 2 - ввести данные вручную): ")

    if mode == '1':
        url = "https://dzen.ru/?yredirect=true&clid=2506522&win=589"
        phrase = "ФСБ"
    elif mode == '2':
        url, phrase = get_input_from_user()
    else:
        print("Неверный выбор режима.")
        exit()

    result = analyze_website(url, phrase)
    print(json.dumps(result, ensure_ascii=False, indent=4))

    save_result = input("Хотите сохранить результат в файл (да/нет)? ").lower()
    if save_result == 'да':
        filename = input("Введите имя файла (например, result.json): ")
        save_result_to_json(result, filename)
        print(f"Результат сохранен в файл {filename}")

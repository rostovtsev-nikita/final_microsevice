from flask import Flask, request, jsonify, abort
import requests
from bs4 import BeautifulSoup
import Levenshtein
import secrets
import hashlib
import logging
from cachetools import TTLCache, cached
from datetime import datetime

app = Flask(__name__)

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Кэширование
cache = TTLCache(maxsize=100, ttl=3600)

# Список API токенов для авторизации
api_tokens = []
app.config['api_tokens'] = api_tokens


def generate_token(length=32):
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


def hash_token(token):
    sha3_512 = hashlib.sha3_512()
    sha3_512.update(token.encode('utf-8'))
    hashed_token = sha3_512.hexdigest()
    return hashed_token


def fetch_site_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text, response.status_code
    except requests.RequestException as e:
        return str(e), getattr(e.response, 'status_code', None)


def clean_text(text):
    return ''.join(text.split()).lower()


def find_phrase(content, phrase):
    cleaned_content = clean_text(content)
    cleaned_phrase = clean_text(phrase)
    min_distance = len(cleaned_phrase)
    phrase_found = False
    for i in range(len(cleaned_content) - len(cleaned_phrase) + 1):
        sub_string = cleaned_content[i:i + len(cleaned_phrase)]
        distance = Levenshtein.distance(sub_string, cleaned_phrase)
        if distance <= 2:
            phrase_found = True
            min_distance = min(min_distance, distance)
    return phrase_found, min_distance


@app.route('/generate_token', methods=['POST'])
def generate_token_endpoint():
    token = generate_token()
    hashed_token = hash_token(token)
    api_tokens.append(hashed_token)
    app.logger.info(f"Generated token: {token} (hashed: {hashed_token})")
    app.logger.info(f"Current tokens: {api_tokens}")
    return jsonify({"token": token})


def log_request(params, result):
    logging.info(f"Params: {params} - Result: {result}")


@cached(cache)
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


@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    if 'Authorization' not in request.headers:
        app.logger.error("Authorization header missing")
        abort(401)
    token = request.headers['Authorization']
    hashed_token = hash_token(token)
    if hashed_token not in api_tokens:
        app.logger.error("Invalid token")
        abort(403)

    try:
        data = request.get_json()
        if not data or 'url' not in data or 'phrase' not in data:
            app.logger.error("Invalid JSON data")
            abort(400)
    except Exception as e:
        app.logger.error(f"Failed to decode JSON object: {str(e)}")
        abort(400)

    url = data['url']
    phrase = data['phrase']

    app.logger.info(f"Analyzing URL: {url} with phrase: {phrase}")

    result = analyze_website(url, phrase)
    log_request({"url": url, "phrase": phrase}, result)
    return jsonify(result)



if __name__ == '__main__':
    app.run(threaded=True, debug=True)

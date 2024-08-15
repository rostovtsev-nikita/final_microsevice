import unittest
import json
from microservice import app, generate_token, hash_token


class FlaskMicroserviceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Генерируем токен и хэшируем его
        self.token = generate_token()
        self.hashed_token = hash_token(self.token)
        # Добавляем хэшированный токен в список токенов
        with app.app_context():
            app.config['api_tokens'].append(self.hashed_token)

    def test_generate_token(self):
        response = self.app.post('/generate_token')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn('token', data)
        self.assertEqual(len(data['token']), 32)

    def test_analyze_website(self):
        url = "https://en.wikipedia.org/wiki/Levenshtein_distance"
        phrase = "Levenshtein distance"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0"
        }
        data = {
            "url": url,
            "phrase": phrase
        }
        response = self.app.post('/analyze', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode())
        self.assertIn('phrase_found', response_data)
        self.assertIn('levenshtein_distance', response_data)

    def test_analyze_website_invalid_token(self):
        url = "https://en.wikipedia.org/wiki/Levenshtein_distance"
        phrase = "Levenshtein distance"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "invalid_token",
            "User-Agent": "Mozilla/5.0"
        }
        data = {
            "url": url,
            "phrase": phrase
        }
        response = self.app.post('/analyze', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 403)

    def test_analyze_website_missing_token(self):
        url = "https://en.wikipedia.org/wiki/Levenshtein_distance"
        phrase = "Levenshtein distance"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        data = {
            "url": url,
            "phrase": phrase
        }
        response = self.app.post('/analyze', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 401)

    def test_analyze_website_invalid_json(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0"
        }
        data = "invalid_json"
        response = self.app.post('/analyze', headers=headers, data=data)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
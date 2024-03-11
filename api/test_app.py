import unittest
from unittest.mock import patch, MagicMock
from app import fetch_github_content, convert_md_to_html, extract_tags_from_html

class TestUtils(unittest.TestCase):
    @patch('app.req.get')
    def test_fetch_github_content(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'content': 'SGVsbG8sIFdvcmxkIQ=='}
        mock_get.return_value = mock_response

        result = fetch_github_content('https://fakeurl.com')
        self.assertEqual(result, 'Hello, World!')

    def test_convert_md_to_html(self):
        markdown_content = "# Hello\nThis is markdown."
        html_content = convert_md_to_html(markdown_content)
        self.assertIn("<h1>Hello</h1>", html_content)
        self.assertIn("<p>This is markdown.</p>", html_content)

    def test_extract_tags_from_html(self):
        html_content = "<table><tbody><tr><td>Tag1</td><td><ul><li>Item1</li><li>Item2</li></ul></td></tr></tbody></table>"
        tags = extract_tags_from_html(html_content)
        self.assertIn("Tag1", tags)
        self.assertEqual(tags["Tag1"], ["Item1", "Item2"])

### Testing Flask Routes

class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        from app import app
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.fetch_github_content')
    @patch('app.extract_tags_from_html')
    def test_tags_route(self, mock_extract, mock_fetch):
        mock_fetch.return_value = "Markdown Content"
        mock_extract.return_value = {"Tag1": ["Item1", "Item2"]}
        response = self.app.get('/tags')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag1', response.data)
        self.assertIn(b'Item1', response.data)
        self.assertIn(b'Item2', response.data)

    # You can add more tests for other routes and utility functions...

if __name__ == '__main__':
    unittest.main()

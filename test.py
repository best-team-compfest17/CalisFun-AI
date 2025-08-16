import unittest
import json
import io
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image

# Test-specific imports
from app import create_app, preprocess_image

class FlaskAPITestCase(unittest.TestCase):
    def setUp(self):
        # Configure all mocks first
        self.mock_processor = MagicMock()
        self.mock_model = MagicMock()
        self.mock_azure = MagicMock()
        
        # Patch the actual implementations
        self.patcher1 = patch('app.TrOCRProcessor.from_pretrained', return_value=self.mock_processor)
        self.patcher2 = patch('app.VisionEncoderDecoderModel.from_pretrained', return_value=self.mock_model)
        self.patcher3 = patch('app.AzureOpenAI', return_value=self.mock_azure)
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        
        # Create test app with mocks
        self.app = create_app()
        self.client = self.app.test_client()
        
        # Configure mock behaviors
        self.mock_pixel_values = MagicMock()
        self.mock_processor.return_value = self.mock_pixel_values
        self.mock_model.generate.return_value = ["mocked_ids"]
        self.mock_processor.batch_decode.return_value = ["mocked text"]
        
        # Mock Azure response
        self.mock_response = MagicMock()
        self.mock_choice = MagicMock()
        self.mock_choice.message.content = "Mocked reply"
        self.mock_response.choices = [self.mock_choice]
        self.mock_response.usage = MagicMock()
        self.mock_response.usage.total_tokens = 42
        self.mock_azure.chat.completions.create.return_value = self.mock_response
        
        # Test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.image_bytes = io.BytesIO()
        self.test_image.save(self.image_bytes, format='PNG')
        self.image_bytes.seek(0)

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()

    def test_healthz(self):
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'ok')

    @patch('app.preprocess_image', return_value=np.array([[1, 2], [3, 4]], dtype=np.uint8))
    def test_ocr_success(self, mock_preprocess):
        # Processor should return an object with .pixel_values
        mock_output = MagicMock()
        mock_output.pixel_values = "mocked_pixels"
        self.mock_processor.return_value = mock_output

        # Mock model + processor behavior
        self.mock_model.generate.return_value = ["mocked_ids"]
        self.mock_processor.batch_decode.return_value = ["mocked text"]

        response = self.client.post(
            '/ocr',
            data={'file': (self.image_bytes, 'test.png')},
            content_type='multipart/form-data'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['text'], 'mocked text')

        # Verify preprocess called
        mock_preprocess.assert_called_once()

        # Verify pipeline executed correctly
        self.mock_processor.assert_called_once()
        self.mock_model.generate.assert_called_once()  # don’t force exact arg check
        self.mock_processor.batch_decode.assert_called_once_with(["mocked_ids"], skip_special_tokens=True)

    def test_ocr_no_file(self):
        response = self.client.post('/ocr')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['error'], 'No file uploaded')

    def test_ocr_empty_filename(self):
        response = self.client.post(
            '/ocr',
            data={'file': (io.BytesIO(b''), '')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['error'], 'Empty filename')

    def test_chat_success(self):
        response = self.client.post(
            '/chat',
            data=json.dumps({"message": "Hello"}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['reply'], 'Mocked reply')
        self.assertEqual(data['tokens_used'], 42)

    def test_chat_no_message(self):
        response = self.client.post(
            '/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['error'], 'Message is required')

if __name__ == '__main__':
    unittest.main()
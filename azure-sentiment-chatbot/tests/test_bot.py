import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
from bot import Chatbot, AzureAnalyzer, Sentiment, ServiceUnavailable
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError

class RouterTests(unittest.TestCase):
    def setUp(self):
        self.fake = Mock()
        self.fake.analyze.return_value = Sentiment('positive', .99, .005, .005)
        self.bot = Chatbot(self.fake)

    def test_local_commands_never_call_cloud(self):
        for text in ['help', 'capabilities', 'examples', 'about', 'hello', 'quit']:
            self.assertTrue(self.bot.reply(text))
        self.fake.analyze.assert_not_called()

    def test_malformed_input_never_calls_cloud(self):
        for text in ['', '   ', None, 123, '!!!', 'sentiment:', '/unknown', 'a'*1001, 'bad\x1btext']:
            self.assertTrue(self.bot.reply(text))
        self.fake.analyze.assert_not_called()

    def test_multiple_prompts(self):
        for text in ['I love this.', 'sentiment: Delivery was late.', 'The shop opens at nine.']:
            self.assertIn('Azure sentiment:', self.bot.reply(text))
        self.assertEqual(self.fake.analyze.call_count, 3)
        self.assertEqual(self.fake.analyze.call_args_list[1].args, ('Delivery was late.',))

    def test_maximum_boundary(self):
        self.bot.reply('a'*1000)
        self.fake.analyze.assert_called_once()

    def test_recovery_after_failure(self):
        self.fake.analyze.side_effect = [ServiceUnavailable('Temporarily unavailable'), Sentiment('neutral', .1, .8, .1)]
        self.assertEqual(self.bot.reply('One sentence.'), 'Temporarily unavailable')
        self.assertIn('neutral', self.bot.reply('Another sentence.'))

class AdapterTests(unittest.TestCase):
    def test_success_mapping(self):
        client = Mock()
        client.analyze_sentiment.return_value = [NS(is_error=False, sentiment='mixed', confidence_scores=NS(positive=.4, neutral=.1, negative=.5))]
        self.assertEqual(AzureAnalyzer(client).analyze('Good and bad.').label, 'mixed')
        client.analyze_sentiment.assert_called_once_with(documents=['Good and bad.'], language='en', logging_enable=False)

    @patch.dict('os.environ', {}, clear=True)
    def test_missing_credentials(self):
        with self.assertRaisesRegex(ServiceUnavailable, 'not configured'):
            AzureAnalyzer().analyze('Test')

    @patch.dict('os.environ', {'AZURE_LANGUAGE_KEY':'test', 'AZURE_LANGUAGE_ENDPOINT':'http://unsafe.example'})
    def test_invalid_endpoint(self):
        with self.assertRaisesRegex(ServiceUnavailable, 'HTTPS'):
            AzureAnalyzer().analyze('Test')

    def test_document_error(self):
        client = Mock()
        client.analyze_sentiment.return_value = [NS(is_error=True)]
        with self.assertRaisesRegex(ServiceUnavailable, 'could not analyze'):
            AzureAnalyzer(client).analyze('Test')

    def test_http_errors_redact_details(self):
        for status, expected in [(401,'denied'),(403,'denied'),(429,'quota'),(500,'resource status')]:
            with self.subTest(status=status):
                exc = HttpResponseError('SECRET request details')
                exc.status_code = status
                client = Mock()
                client.analyze_sentiment.side_effect = exc
                with self.assertRaises(ServiceUnavailable) as caught:
                    AzureAnalyzer(client).analyze('Test')
                self.assertIn(expected, str(caught.exception))
                self.assertNotIn('SECRET', str(caught.exception))

    def test_network_errors(self):
        for error in (ServiceRequestError, ServiceResponseError):
            client = Mock()
            client.analyze_sentiment.side_effect = error('private details')
            with self.assertRaisesRegex(ServiceUnavailable, 'timed out'):
                AzureAnalyzer(client).analyze('Test')

if __name__ == '__main__':
    unittest.main()

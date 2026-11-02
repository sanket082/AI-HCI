"""Traditional command router plus Azure AI Language sentiment analysis."""
from dataclasses import dataclass
import os
from urllib.parse import urlparse

MAX_CHARS = 1000
HELP = ('Commands: help, capabilities, examples, about, quit. '
        'Use sentiment: <English text> or type a sentence to analyze it. '
        'Limit: 1000 characters. Text for analysis is sent to Azure; avoid personal data.')

class ServiceUnavailable(Exception):
    """Safe, user-facing error without credentials or request content."""

@dataclass(frozen=True)
class Sentiment:
    label: str
    positive: float
    neutral: float
    negative: float

class AzureAnalyzer:
    """Lazy connection allows traditional commands without credentials."""
    def __init__(self, client=None):
        self.client = client

    def analyze(self, text):
        try:
            from azure.ai.textanalytics import TextAnalyticsClient
            from azure.core.credentials import AzureKeyCredential
            from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError
        except ImportError:
            raise ServiceUnavailable('Install dependencies with: pip install -r requirements.txt') from None
        if self.client is None:
            key = os.environ.get('AZURE_LANGUAGE_KEY', '').strip()
            endpoint = os.environ.get('AZURE_LANGUAGE_ENDPOINT', '').strip()
            if not key or not endpoint:
                raise ServiceUnavailable('Azure is not configured. Set AZURE_LANGUAGE_KEY and AZURE_LANGUAGE_ENDPOINT.')
            u = urlparse(endpoint)
            if u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment:
                raise ServiceUnavailable('Set a valid HTTPS endpoint copied from your Azure Language resource.')
            self.client = TextAnalyticsClient(endpoint, AzureKeyCredential(key),
                retry_total=0, connection_timeout=5, read_timeout=15)
        try:
            results = self.client.analyze_sentiment(documents=[text], language='en', logging_enable=False)
            result = results[0]
            if result.is_error:
                raise ServiceUnavailable('Azure could not analyze that text. Try a shorter English sentence.')
            s = result.confidence_scores
            return Sentiment(result.sentiment, s.positive, s.neutral, s.negative)
        except HttpResponseError as exc:
            status = exc.status_code
            if status in (401, 403):
                msg = 'Azure access was denied. Check the key and matching resource endpoint.'
            elif status == 429:
                msg = 'Azure rate or quota limit reached. Wait before trying again; check F0 usage.'
            else:
                msg = 'Azure could not complete the request. Check resource status and try again later.'
            raise ServiceUnavailable(msg) from None
        except (ServiceRequestError, ServiceResponseError):
            raise ServiceUnavailable('Azure connection failed or timed out. Check the network and try again.') from None

class Chatbot:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer if analyzer is not None else AzureAnalyzer()

    def reply(self, message):
        if not isinstance(message, str):
            return 'Please enter text, not another data type.'
        message = message.strip()
        if not message:
            return 'Please enter a message. Type help for options.'
        if any(ord(c) < 32 and c not in '\n\t' for c in message) or '\x7f' in message:
            return 'Please remove control characters and try again.'
        lowered = message.casefold()
        if lowered in ('help', 'capabilities', '/help'):
            return HELP
        if lowered in ('hi', 'hello', 'hey'):
            return 'Hello! I can analyze the sentiment of English text. Type help to begin.'
        if lowered == 'about':
            return 'I combine local rules with Azure AI Language. I classify text; I am not a general question-answering assistant.'
        if lowered == 'examples':
            return 'Try: sentiment: I love this service. | sentiment: My delivery was late. | sentiment: The shop opens at nine.'
        if lowered in ('quit', 'exit', '/quit'):
            return 'Goodbye!'
        if lowered.startswith('sentiment:'):
            message = message.split(':', 1)[1].strip()
        elif lowered.startswith('/'):
            return 'Unknown command. Type help for supported commands.'
        if not message or not any(c.isalpha() for c in message):
            return 'Please include words in the English text you want analyzed.'
        if len(message) > MAX_CHARS:
            return 'Please shorten the text to 1000 characters or fewer.'
        try:
            result = self.analyzer.analyze(message)
        except ServiceUnavailable as exc:
            return str(exc)
        return (f'Azure sentiment: {result.label}. Confidence scores: '
                f'positive={result.positive:.3f}, neutral={result.neutral:.3f}, negative={result.negative:.3f}. '
                'This is a model estimate about the text, not a judgment about you.')

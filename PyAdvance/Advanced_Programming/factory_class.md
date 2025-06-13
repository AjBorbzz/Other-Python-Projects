# Real-World Use Cases of Factory Pattern in Python

Here are the most common real-world use cases of the Factory Pattern in Python:

## 1. Database Connection Management

Different databases but same interface:

```python
class DatabaseFactory:
    @staticmethod
    def create_connection(db_type: str, **config):
        if db_type == "postgresql":
            return PostgreSQLConnection(config)
        elif db_type == "mysql":
            return MySQLConnection(config)
        elif db_type == "sqlite":
            return SQLiteConnection(config)
        
# Usage based on environment
db = DatabaseFactory.create_connection(
    os.getenv("DB_TYPE", "sqlite"),
    host="localhost", port=5432
)
```

## 2. File Format Parsers

Handle different file types with unified interface:

```python
class DocumentParserFactory:
    parsers = {
        '.pdf': PDFParser,
        '.docx': WordParser,
        '.txt': TextParser,
        '.csv': CSVParser,
    }
    
    @classmethod
    def create_parser(cls, file_path: str):
        extension = Path(file_path).suffix.lower()
        parser_class = cls.parsers.get(extension)
        if not parser_class:
            raise ValueError(f"Unsupported file type: {extension}")
        return parser_class(file_path)

# Usage
parser = DocumentParserFactory.create_parser("report.pdf")
content = parser.extract_text()
```

## 3. Payment Processing

Different payment gateways:

```python
class PaymentProcessorFactory:
    @staticmethod
    def create_processor(provider: str, **credentials):
        if provider == "stripe":
            return StripeProcessor(credentials['api_key'])
        elif provider == "paypal":
            return PayPalProcessor(credentials['client_id'], credentials['secret'])
        elif provider == "square":
            return SquareProcessor(credentials['app_id'])

# Usage
processor = PaymentProcessorFactory.create_processor(
    provider=user_preference,
    api_key=config['stripe_key']
)
result = processor.charge(amount=100.00, card_token="tok_123")
```

## 4. Notification Systems

Multiple communication channels:

```python
class NotificationFactory:
    @staticmethod
    def create_notifier(channel: str, **config):
        if channel == "email":
            return EmailNotifier(config['smtp_server'], config['credentials'])
        elif channel == "slack":
            return SlackNotifier(config['webhook_url'])
        elif channel == "sms":
            return SMSNotifier(config['twilio_credentials'])

# Send notifications through different channels
for channel in user.notification_preferences:
    notifier = NotificationFactory.create_notifier(channel, **settings)
    notifier.send("Your order has shipped!")
```

## 5. Testing: Mock vs Real Objects

Switch between real and test implementations:

```python
class ServiceFactory:
    @staticmethod
    def create_email_service(environment: str):
        if environment == "test":
            return MockEmailService()  # Doesn't actually send emails
        elif environment == "development":
            return ConsoleEmailService()  # Prints to console
        else:
            return SMTPEmailService()  # Real email sending

# In your app
email_service = ServiceFactory.create_email_service(
    os.getenv("ENVIRONMENT", "production")
)
```

## 6. Data Serialization

Different output formats:

```python
class SerializerFactory:
    serializers = {
        'json': JSONSerializer,
        'xml': XMLSerializer,
        'yaml': YAMLSerializer,
        'csv': CSVSerializer,
    }
    
    @classmethod
    def create_serializer(cls, format_type: str):
        return cls.serializers[format_type]()

# API endpoint that supports multiple formats
def export_data(request):
    format_type = request.GET.get('format', 'json')
    serializer = SerializerFactory.create_serializer(format_type)
    return serializer.serialize(data)
```

## 7. Machine Learning Models

Different algorithms for same task:

```python
class ModelFactory:
    @staticmethod
    def create_classifier(algorithm: str, **params):
        if algorithm == "random_forest":
            return RandomForestClassifier(**params)
        elif algorithm == "svm":
            return SVMClassifier(**params)
        elif algorithm == "neural_network":
            return NeuralNetworkClassifier(**params)

# Usage
model = ModelFactory.create_classifier(
    algorithm=config['model_type'],
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)
```

## 8. Web Framework Adapters

Supporting multiple web frameworks:

```python
class WebAdapterFactory:
    @staticmethod
    def create_adapter(framework: str):
        if framework == "flask":
            return FlaskAdapter()
        elif framework == "django":
            return DjangoAdapter()
        elif framework == "fastapi":
            return FastAPIAdapter()

# Your library can work with different frameworks
adapter = WebAdapterFactory.create_adapter(detected_framework)
adapter.register_routes(my_routes)
```

## When to Use Factory Pattern

The Factory Pattern is particularly useful when you need to:

- Hide complex object creation logic
- Choose implementations at runtime based on configuration
- Support multiple similar services/providers
- Make testing easier with mock objects
- Keep your code flexible and maintainable

It's especially common in libraries, frameworks, and applications that need to support multiple backends or implementations.
class TestConfig:
    """Configuration for testing."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Using SQLite in memory for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test_secret"
    TESTING = True

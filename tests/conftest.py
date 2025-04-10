import pytest
from app import create_app, db
from app.models.blacklist import Blacklist
from tests.test_config import TestConfig
from tests.db_mock import MockDB
from unittest import mock

# Create a global mock database instance
mock_db = MockDB()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up the test database once for the entire test session"""
    # Import the SQLAlchemy Base that contains all model definitions
    from app import db
    
    # Create the tables in our mock database
    mock_db.create_tables(db.Model)
    
    yield
    
    # Teardown - not strictly necessary since we're using in-memory DB

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing"""
    # Create the Flask application
    app = create_app()
    app.config.from_object(TestConfig)
    
    yield app

@pytest.fixture(autouse=True)
def setup_db_session(app):
    """Set up a fresh database session for each test"""
    # Create a mock session
    mock_session = mock_db.setup()
    
    # Patch db.session with our mock session
    with mock.patch.object(db, 'session', mock_session):
        yield
        
        # Clean up - use our teardown instead of calling remove directly
        mock_db.teardown()

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def valid_headers(app):
    """Headers with valid authentication token"""
    return {'Authorization': f'Bearer {app.config["STATIC_TOKEN"]}'}

@pytest.fixture
def invalid_headers():
    """Headers with invalid authentication token"""
    return {'Authorization': 'Bearer invalid_token'}

@pytest.fixture
def sample_blacklist_entry(app):
    """Create a sample blacklist entry"""
    with app.app_context():
        # Create new entry
        entry = Blacklist(
            email="blacklisted@example.com",
            app_uuid="123e4567-e89b-12d3-a456-426614174000",
            blocked_reason="Test reason",
            request_ip="127.0.0.1"
        )
        db.session.add(entry)
        db.session.commit()
        
        # Return a dict with the data we need
        return {"email": entry.email, "blocked_reason": entry.blocked_reason}

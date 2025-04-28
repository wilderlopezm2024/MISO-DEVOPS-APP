import json
import pytest
from app import db
from app.models.blacklist import Blacklist


class TestPingEndpoint:
    def test_ping_endpoint(self, client):
        """Test the ping endpoint returns pong"""
        response = client.get('/ping')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'pong'


class TestAuthenticationRequired:
    """Test that endpoints require authentication"""
    
    def test_blacklist_post_requires_auth(self, client):
        """Test POST /blacklists requires auth"""
        response = client.post('/blacklists', 
                              json={'email': 'test@example.com', 'app_uuid': '123'})
        assert response.status_code == 401
        
    def test_blacklist_get_requires_auth(self, client):
        """Test GET /blacklists/<email> requires auth"""
        response = client.get('/blacklists/test@example.com')
        assert response.status_code == 401
        
    def test_reset_requires_auth(self, client):
        """Test POST /reset requires auth"""
        response = client.post('/reset')
        assert response.status_code == 401
        
    def test_invalid_token_rejected(self, client, invalid_headers):
        """Test requests with invalid tokens are rejected"""
        response = client.get('/blacklists/test@example.com', headers=invalid_headers)
        assert response.status_code == 401


class TestBlacklistPost:
    """Test the blacklist POST endpoint"""
    
    def test_add_email_to_blacklist(self, client, valid_headers, app):
        """Test adding a new email to the blacklist"""
        payload = {
            'email': 'new@example.com',
            'app_uuid': '123e4567-e89b-12d3-a456-426614174000',
            'blocked_reason': 'Test reason'
        }
        
        response = client.post(
            '/blacklists',
            json=payload,
            headers=valid_headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Email successfully blacklisted'
        assert data['data']['email'] == payload['email']
        assert data['data']['app_uuid'] == payload['app_uuid']
        assert data['data']['blocked_reason'] == payload['blocked_reason']
        
        # Verify entry was created in database
        with app.app_context():
            entry = Blacklist.query.filter_by(email=payload['email']).first()
            assert entry is not None
            assert entry.app_uuid == payload['app_uuid']
    
    def test_add_duplicate_email(self, client, valid_headers, sample_blacklist_entry, app):
        """Test that adding a duplicate email returns 400"""
        payload = {
            'email': sample_blacklist_entry['email'],  # Now using dict instead of object
            'app_uuid': '123e4567-e89b-12d3-a456-426614174000'
        }
        
        response = client.post(
            '/blacklists',
            json=payload,
            headers=valid_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Email already blacklisted'
    
    def test_missing_required_fields(self, client, valid_headers):
        """Test that missing required fields returns 400"""
        # Missing email
        response = client.post(
            '/blacklists',
            json={'app_uuid': '123'},
            headers=valid_headers
        )
        assert response.status_code == 400
        
        # Missing app_uuid
        response = client.post(
            '/blacklists',
            json={'email': 'test@example.com'},
            headers=valid_headers
        )
        assert response.status_code == 400


class TestBlacklistGet:
    """Test the blacklist GET endpoint"""
    
    def test_get_blacklisted_email(self, client, valid_headers, sample_blacklist_entry, app):
        """Test getting a blacklisted email returns status=true"""
        # Using the dict values directly
        email = sample_blacklist_entry['email']
        blocked_reason = sample_blacklist_entry['blocked_reason']
        
        response = client.get(
            f'/blacklists/{email}',
            headers=valid_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['blocked'] == True
        assert data['email'] == email
        assert data['blocked_reason'] == blocked_reason
    
    def test_get_non_blacklisted_email(self, client, valid_headers):
        """Test getting a non-blacklisted email returns status=false"""
        email = 'nonblacklisted@example.com'
        
        response = client.get(
            f'/blacklists/{email}',
            headers=valid_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['blocked'] == False
        assert data['email'] == email
        assert data['blocked_reason'] is None


class TestResetEndpoint:
    """Test the reset endpoint"""
    
    def test_reset_database(self, client, valid_headers, sample_blacklist_entry, app):
        """Test that reset endpoint clears the database"""
        # Confirm the test entry exists - note we're using a fresh session in app context
        with app.app_context():
            count = Blacklist.query.count()
            assert count > 0
        
        response = client.post('/reset', headers=valid_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Database reset successfully'

class TestForcedFailure:
    """Clase creada para forzar el fallo en el pipeline"""

    def test_fail_on_purpose(self):
        """Esta prueba falla intencionalmente"""
        assert 1 == 0  

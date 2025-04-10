import os
from unittest import mock
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

class MockDB:
    """Mock database for testing purposes"""
    
    def __init__(self, db_uri='sqlite:///:memory:?cache=shared'):
        """Initialize mock database with SQLite in-memory by default
           Using ?cache=shared to ensure the database persists across connections"""
        self.engine = create_engine(db_uri)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.connection = None
        self.transaction = None
        self.tables_created = False
        
    def setup(self):
        """Set up the database for a test"""
        # Connect to the database and begin a transaction
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        
        # Create a scoped session to mimic Flask-SQLAlchemy behavior
        session = scoped_session(self.session_factory)
        session.configure(bind=self.connection)
        
        # Add a remove method if not present (to avoid errors later)
        if not hasattr(session, 'remove'):
            session.remove = lambda: None
            
        return session
    
    def teardown(self):
        """Tear down the database after a test"""
        # Close the session
        if hasattr(self.Session, 'remove'):
            self.Session.remove()
            
        # Rollback transaction and close connection
        if self.transaction:
            self.transaction.rollback()
        if self.connection:
            self.connection.close()
            
    def create_tables(self, base):
        """Create all tables defined in SQLAlchemy Base"""
        if not self.tables_created:
            base.metadata.create_all(self.engine)
            self.tables_created = True

def patch_db_connection():
    """Patch SQLAlchemy to use our mock database"""
    # This function returns a context manager that can be used in tests
    patcher = mock.patch('app.db', create=True)
    return patcher

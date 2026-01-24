import pytest
from sqlalchemy import text
from api.models import PromptRequest
from db.database import engine, init_db, SessionLocal, Base
from db.models import Conversation

class TestSecurityValidation:
    """Test security-related input validation"""

    def setup_method(self):
        # Drop all tables to ensure clean slate
        Base.metadata.drop_all(bind=engine)
        init_db()
        self.session = SessionLocal()

    def teardown_method(self):
        self.session.close()

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # This should be handled by parameterized queries
        malicious = "admin' OR '1'='1"
        # Should not raise, but should be safely escaped in queries
        request = PromptRequest(prompt=malicious)

        # Verify it's sanitized/handled safely by the ORM/DB layer

        # Scenario 1: Using ORM (implicitly parameterized)
        conv = Conversation(user_id=1, title="Safe Chat", last_prompt=request.prompt)
        self.session.add(conv)
        self.session.commit()

        saved_conv = self.session.query(Conversation).filter_by(last_prompt=malicious).first()
        assert saved_conv is not None
        assert saved_conv.last_prompt == malicious

        # Scenario 2: Using parameterized raw SQL (explicitly safe)
        # This demonstrates the "solution" of using parameters instead of concatenation
        query = text("SELECT * FROM conversations WHERE last_prompt = :prompt")
        result = self.session.execute(query, {"prompt": malicious}).fetchone()

        assert result is not None
        assert result.last_prompt == malicious

    def test_sql_injection_vulnerability_demonstration(self):
        """
        Demonstrate what we are PREVENTING.
        This test is just to show that the malicious string is indeed capable of injection
        if misused (e.g. string concatenation).
        """
        malicious = "admin' OR '1'='1"

        # NOTE: In SQLite 'admin' OR '1'='1' doesn't magically return all rows if checked against a text field
        # unless constructed specifically to break the query logic.

        # Let's try to simulate a vulnerable query construction
        # Vulnerable: SELECT * FROM conversations WHERE last_prompt = 'admin' OR '1'='1'

        # We need data in the DB first
        conv = Conversation(user_id=1, title="Real Chat", last_prompt="Safe")
        self.session.add(conv)
        self.session.commit()

        # Construct vulnerable SQL
        # This is what we are avoiding!
        unsafe_sql = f"SELECT * FROM conversations WHERE last_prompt = '{malicious}'"

        # If we run this, it effectively becomes: SELECT ... WHERE last_prompt = 'admin' OR '1'='1'
        # Which is always true for '1'='1', so it should return the row even if prompt doesn't match

        result = self.session.execute(text(unsafe_sql)).fetchall()

        # Verify that we got results (injection successful)
        assert len(result) > 0

        # But when we use the SAFE method (parameterized), it should NOT return the row (unless it actually matches)
        safe_query = text("SELECT * FROM conversations WHERE last_prompt = :prompt")
        result_safe = self.session.execute(safe_query, {"prompt": malicious}).fetchall()

        # Should be empty because no row has "admin' OR '1'='1" as the prompt content
        assert len(result_safe) == 0

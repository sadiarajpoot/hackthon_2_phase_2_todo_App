"""
Database indexing for optimized queries.
Sets up proper indexing for the chat API based on access patterns.
"""
from sqlmodel import Session
from sqlalchemy import text
from typing import List
import os


class DatabaseIndexOptimizer:
    """
    Class to manage database indexing for optimized queries.
    Creates proper indexes based on access patterns identified in the data model.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_indexes(self):
        """
        Create all necessary database indexes for optimal performance.
        Based on the access patterns defined in the data model.
        """
        # Create indexes for Conversation table
        self._create_conversation_indexes()

        # Create indexes for Message table
        self._create_message_indexes()

        # Create indexes for Task table (existing from Phase II)
        self._create_task_indexes()

    def _create_conversation_indexes(self):
        """
        Create indexes for the Conversation table based on access patterns.
        """
        try:
            # Index on user_id for efficient user conversation retrieval
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_conversation_user_id
                ON conversation (user_id)
            """))

            # Index on updated_at for sorting by recency
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_conversation_updated_at
                ON conversation (updated_at DESC)
            """))

            # Index on created_at for chronological queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_conversation_created_at
                ON conversation (created_at DESC)
            """))

            # Combined index for user and timestamp queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_conversation_user_updated
                ON conversation (user_id, updated_at DESC)
            """))

            self.db_session.commit()
            print("Conversation indexes created successfully")
        except Exception as e:
            print(f"Error creating conversation indexes: {str(e)}")
            self.db_session.rollback()
            raise

    def _create_message_indexes(self):
        """
        Create indexes for the Message table based on access patterns.
        """
        try:
            # Index on conversation_id for efficient conversation message retrieval
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_message_conversation_id
                ON message (conversation_id)
            """))

            # Index on sequence_number for ordered retrieval
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_message_sequence_number
                ON message (conversation_id, sequence_number)
            """))

            # Index on timestamp for chronological access
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_message_timestamp
                ON message (conversation_id, timestamp)
            """))

            # Index on role for filtering by message sender
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_message_role
                ON message (conversation_id, role)
            """))

            # Combined index for conversation and role queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_message_conversation_role
                ON message (conversation_id, role, sequence_number)
            """))

            self.db_session.commit()
            print("Message indexes created successfully")
        except Exception as e:
            print(f"Error creating message indexes: {str(e)}")
            self.db_session.rollback()
            raise

    def _create_task_indexes(self):
        """
        Create indexes for the Task table based on access patterns.
        """
        try:
            # Index on user_id for efficient user task retrieval
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_task_user_id
                ON task (user_id)
            """))

            # Index on status for filtering tasks by status
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_task_status
                ON task (user_id, status)
            """))

            # Index on created_at for chronological queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_task_created_at
                ON task (created_at DESC)
            """))

            # Index on updated_at for recency-based queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_task_updated_at
                ON task (updated_at DESC)
            """))

            # Combined index for user and status queries
            self.db_session.exec(text("""
                CREATE INDEX IF NOT EXISTS ix_task_user_status
                ON task (user_id, status, updated_at DESC)
            """))

            self.db_session.commit()
            print("Task indexes created successfully")
        except Exception as e:
            print(f"Error creating task indexes: {str(e)}")
            self.db_session.rollback()
            raise

    def validate_indexes(self) -> dict:
        """
        Validate that all required indexes exist in the database.

        Returns:
            Dictionary with validation results for each table
        """
        results = {
            "conversations": {},
            "messages": {},
            "tasks": {}
        }

        # Check conversation indexes
        try:
            conv_indexes = self.db_session.exec(text("""
                SELECT indexname FROM pg_indexes WHERE tablename = 'conversation'
            """)).all()
            conv_index_names = [idx[0] for idx in conv_indexes if idx]

            required_conv_indexes = [
                "ix_conversation_user_id",
                "ix_conversation_updated_at",
                "ix_conversation_created_at",
                "ix_conversation_user_updated"
            ]

            for idx_name in required_conv_indexes:
                results["conversations"][idx_name] = idx_name in conv_index_names

        except Exception as e:
            print(f"Error checking conversation indexes: {str(e)}")
            results["conversations"]["error"] = str(e)

        # Check message indexes
        try:
            msg_indexes = self.db_session.exec(text("""
                SELECT indexname FROM pg_indexes WHERE tablename = 'message'
            """)).all()
            msg_index_names = [idx[0] for idx in msg_indexes]

            required_msg_indexes = [
                "ix_message_conversation_id",
                "ix_message_sequence_number",
                "ix_message_timestamp",
                "ix_message_role",
                "ix_message_conversation_role"
            ]

            for idx_name in required_msg_indexes:
                results["messages"][idx_name] = idx_name in msg_index_names

        except Exception as e:
            print(f"Error checking message indexes: {str(e)}")
            results["messages"]["error"] = str(e)

        # Check task indexes
        try:
            task_indexes = self.db_session.exec(text("""
                SELECT indexname FROM pg_indexes WHERE tablename = 'task'
            """)).all()
            task_index_names = [idx[0] for idx in task_indexes]

            required_task_indexes = [
                "ix_task_user_id",
                "ix_task_status",
                "ix_task_created_at",
                "ix_task_updated_at",
                "ix_task_user_status"
            ]

            for idx_name in required_task_indexes:
                results["tasks"][idx_name] = idx_name in task_index_names

        except Exception as e:
            print(f"Error checking task indexes: {str(e)}")
            results["tasks"]["error"] = str(e)

        return results

    def drop_indexes(self):
        """
        Drop all indexes created by this optimizer.
        Use with caution - primarily for development/testing.
        """
        try:
            # Drop conversation indexes
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_conversation_user_id"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_conversation_updated_at"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_conversation_created_at"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_conversation_user_updated"))

            # Drop message indexes
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_message_conversation_id"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_message_sequence_number"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_message_timestamp"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_message_role"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_message_conversation_role"))

            # Drop task indexes
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_task_user_id"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_task_status"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_task_created_at"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_task_updated_at"))
            self.db_session.exec(text("DROP INDEX IF EXISTS ix_task_user_status"))

            self.db_session.commit()
            print("Indexes dropped successfully")
        except Exception as e:
            print(f"Error dropping indexes: {str(e)}")
            self.db_session.rollback()
            raise


def setup_optimized_indexes(db_session: Session):
    """
    Convenience function to set up all optimized indexes for the chat API.

    Args:
        db_session: Database session to execute index creation
    """
    optimizer = DatabaseIndexOptimizer(db_session)
    optimizer.create_indexes()
    return optimizer


# For PostgreSQL databases, this is how we'd create the indexes
# In a production system, these would likely be handled by Alembic migrations
def get_index_creation_sql() -> List[str]:
    """
    Get the SQL statements needed to create all required indexes.

    Returns:
        List of SQL statements to create indexes
    """
    return [
        # Conversation indexes
        "CREATE INDEX IF NOT EXISTS ix_conversation_user_id ON conversation (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_conversation_updated_at ON conversation (updated_at DESC);",
        "CREATE INDEX IF NOT EXISTS ix_conversation_created_at ON conversation (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS ix_conversation_user_updated ON conversation (user_id, updated_at DESC);",

        # Message indexes
        "CREATE INDEX IF NOT EXISTS ix_message_conversation_id ON message (conversation_id);",
        "CREATE INDEX IF NOT EXISTS ix_message_sequence_number ON message (conversation_id, sequence_number);",
        "CREATE INDEX IF NOT EXISTS ix_message_timestamp ON message (conversation_id, timestamp);",
        "CREATE INDEX IF NOT EXISTS ix_message_role ON message (conversation_id, role);",
        "CREATE INDEX IF NOT EXISTS ix_message_conversation_role ON message (conversation_id, role, sequence_number);",

        # Task indexes
        "CREATE INDEX IF NOT EXISTS ix_task_user_id ON task (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_task_status ON task (user_id, status);",
        "CREATE INDEX IF NOT EXISTS ix_task_created_at ON task (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS ix_task_updated_at ON task (updated_at DESC);",
        "CREATE INDEX IF NOT EXISTS ix_task_user_status ON task (user_id, status, updated_at DESC);"
    ]
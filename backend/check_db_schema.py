import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.database import engine
from sqlalchemy import inspect
from sqlmodel import SQLModel
from src.models.task import Task
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message

def check_database_schema():
    print("Checking database schema...")

    # Get inspector to examine the database
    inspector = inspect(engine)

    # Get all table names
    table_names = inspector.get_table_names()
    print(f"Tables in database: {table_names}")

    # Check each table's columns
    for table_name in table_names:
        print(f"\n--- Table: {table_name} ---")
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(f"  Column: {col['name']} - Type: {col['type']} - Nullable: {col['nullable']}")
            if 'default' in col:
                print(f"    Default: {col['default']}")

    # Check if tasks table has the status column
    if 'tasks' in table_names:
        tasks_columns = [col['name'] for col in inspector.get_columns('tasks')]
        print(f"\nTasks table columns: {tasks_columns}")

        if 'status' in tasks_columns:
            print("✅ Status column exists in tasks table")
        else:
            print("❌ Status column is missing from tasks table")

    # Check if the expected tables exist
    expected_tables = ['users', 'tasks', 'conversations', 'messages']
    missing_tables = [table for table in expected_tables if table not in table_names]

    if missing_tables:
        print(f"\n❌ Missing tables: {missing_tables}")
    else:
        print("\n✅ All expected tables exist")

    # Create tables that don't exist
    print("\nEnsuring all tables exist...")
    SQLModel.metadata.create_all(engine)

    # Re-check after creation
    table_names_after = inspector.get_table_names()
    print(f"Tables after ensure: {table_names_after}")

    # Check again for the status column after ensuring tables exist
    if 'tasks' in table_names_after:
        tasks_columns_after = [col['name'] for col in inspector.get_columns('tasks')]
        print(f"Tasks table columns after ensure: {tasks_columns_after}")

        if 'status' in tasks_columns_after:
            print("✅ Status column exists in tasks table after ensure")
        else:
            print("❌ Status column is still missing from tasks table after ensure")

            # Try to manually add the status column
            try:
                print("Attempting to manually add status column...")
                with engine.connect() as conn:
                    # Check if column exists first
                    result = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='status'")
                    if not result.fetchone():
                        # Add the column
                        conn.execute("ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
                        conn.commit()
                        print("✅ Successfully added status column to tasks table")
                    else:
                        print("ℹ️  Status column already exists")

                    # Verify the column was added
                    result = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='status'")
                    if result.fetchone():
                        print("✅ Verification: Status column confirmed to exist")
                    else:
                        print("❌ Verification: Status column does not exist after attempt")
            except Exception as e:
                print(f"❌ Error adding status column: {e}")

if __name__ == "__main__":
    check_database_schema()
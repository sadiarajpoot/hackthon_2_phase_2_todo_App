"""
Database migration script for chatbot tables.
Creates Conversation and Message tables for the AI chatbot functionality.
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql
from enum import Enum


# revision identifiers, used by Alembic.
revision = '003_chatbot_tables'
down_revision = '002_existing_tables'  # Assuming there are previous migrations
branch_labels = None
depends_on = None


def upgrade():
    """Create the new tables for chatbot functionality."""
    # Create conversations table
    op.create_table('conversation',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create messages table
    op.create_table('message',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('conversation_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient querying
    op.create_index('ix_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('ix_conversation_updated_at', 'conversation', ['updated_at'])
    op.create_index('ix_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('ix_message_timestamp', 'message', ['timestamp'])
    op.create_index('ix_message_sequence_number', 'message', ['sequence_number'])


def downgrade():
    """Drop the chatbot tables."""
    # Drop indexes first
    op.drop_index('ix_message_sequence_number')
    op.drop_index('ix_message_timestamp')
    op.drop_index('ix_message_conversation_id')
    op.drop_index('ix_conversation_updated_at')
    op.drop_index('ix_conversation_user_id')

    # Drop tables
    op.drop_table('message')
    op.drop_table('conversation')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS messagerole;")
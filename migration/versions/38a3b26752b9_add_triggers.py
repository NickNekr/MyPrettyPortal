"""Add triggers

Revision ID: 38a3b26752b9
Revises: 3dfe06bf8c02
Create Date: 2023-07-17 10:54:51.380891

"""
from alembic import op
from src.config import app_config


# revision identifiers, used by Alembic.
revision = "38a3b26752b9"
down_revision = "3dfe06bf8c02"
branch_labels = None
depends_on = None


def add_trigger_to_table(table_name):
    return f"""
    CREATE OR REPLACE TRIGGER update_changed_time_tr_on_{table_name}
    BEFORE UPDATE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION update_time();
"""


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_time()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.changed_at = NOW(); 
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    for table in app_config.TABLES_LIST:
        op.execute(add_trigger_to_table(table))


def downgrade() -> None:
    op.execute("DROP FUNCTION update_time CASCADE;")

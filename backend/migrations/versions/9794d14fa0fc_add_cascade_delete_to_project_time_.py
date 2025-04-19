"""Add cascade delete to project-time_entry relationship

Revision ID: 9794d14fa0fc
Revises: d42b1d960110
Create Date: 2025-04-19 22:14:02.603865

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9794d14fa0fc'
down_revision = 'd42b1d960110'
branch_labels = None
depends_on = None


def upgrade():
    # Bestehenden Fremdschlüssel löschen
    op.drop_constraint('time_entries_project_id_fkey',
                       'time_entries', type_='foreignkey')

    # Neuen Fremdschlüssel mit ON DELETE CASCADE erstellen
    op.create_foreign_key(
        'time_entries_project_id_fkey',
        'time_entries', 'projects',
        ['project_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Zurück zum ursprünglichen Zustand ohne CASCADE
    op.drop_constraint('time_entries_project_id_fkey',
                       'time_entries', type_='foreignkey')

    # Fremdschlüssel ohne CASCADE wiederherstellen
    op.create_foreign_key(
        'time_entries_project_id_fkey',
        'time_entries', 'projects',
        ['project_id'], ['id']
    )

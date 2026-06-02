"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("repositories", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("full_name", sa.String(255), nullable=False), sa.Column("html_url", sa.String(500), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("pull_requests", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=False), sa.Column("number", sa.Integer(), nullable=False), sa.Column("title", sa.String(500), nullable=False), sa.Column("author", sa.String(255), nullable=False), sa.Column("base_branch", sa.String(255), nullable=False), sa.Column("head_branch", sa.String(255), nullable=False), sa.Column("html_url", sa.String(500), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("repository_id", "number", name="uq_repository_pr_number"))
    op.create_table("reviews", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("pull_request_id", sa.Integer(), sa.ForeignKey("pull_requests.id"), nullable=False), sa.Column("summary_json", sa.JSON(), nullable=False), sa.Column("agent_outputs_json", sa.JSON(), nullable=False), sa.Column("model", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("review_findings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id"), nullable=False), sa.Column("file_path", sa.String(1000), nullable=False), sa.Column("line_start", sa.Integer(), nullable=True), sa.Column("line_end", sa.Integer(), nullable=True), sa.Column("category", sa.String(100), nullable=False), sa.Column("severity", sa.String(50), nullable=False), sa.Column("confidence", sa.Integer(), nullable=False), sa.Column("title", sa.String(500), nullable=False), sa.Column("explanation", sa.Text(), nullable=False), sa.Column("recommended_fix", sa.Text(), nullable=False), sa.Column("agent", sa.String(100), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("feedback", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id"), nullable=False), sa.Column("finding_id", sa.Integer(), sa.ForeignKey("review_findings.id"), nullable=True), sa.Column("rating", sa.Integer(), nullable=False), sa.Column("comment", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("evaluations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id"), nullable=True), sa.Column("prompt_name", sa.String(255), nullable=False), sa.Column("model", sa.String(255), nullable=False), sa.Column("input_json", sa.JSON(), nullable=False), sa.Column("output_json", sa.JSON(), nullable=False), sa.Column("review_feedback", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_repositories_full_name", "repositories", ["full_name"], unique=True)


def downgrade() -> None:
    op.drop_table("evaluations")
    op.drop_table("feedback")
    op.drop_table("review_findings")
    op.drop_table("reviews")
    op.drop_table("pull_requests")
    op.drop_index("ix_repositories_full_name", table_name="repositories")
    op.drop_table("repositories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

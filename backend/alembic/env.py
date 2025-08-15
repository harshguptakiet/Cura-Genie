"""
Alembic environment configuration for CuraGenie database migrations

This file configures the Alembic migration environment and imports all models
to ensure they are available during migrations.
"""

import logging
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our configuration and models
from core.config import config_manager
from db.models import Base
from db.database_manager import db_manager

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = config.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from configuration"""
    return config_manager.get_database_url()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    config.set_main_option("sqlalchemy.url", url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from our configuration
    url = get_url()
    
    # Update the config with our actual database URL
    config.set_main_option("sqlalchemy.url", url)
    
    # Create engine from config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enable autogenerate for development
            compare_type=True,
            compare_server_default=True,
            # Include schema in comparisons
            include_schemas=True,
            # Render as batch for better compatibility
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Import the context object from alembic.runtime.migration
from alembic import context

# Set up logging
logger = logging.getLogger(__name__)

# Log the migration environment setup
logger.info("🔧 Setting up Alembic migration environment")
logger.info(f"📊 Target metadata: {target_metadata}")
logger.info(f"🗄️  Database URL: {get_url()}")

# Set up the context
context.configure(
    target_metadata=target_metadata,
    # Enable autogenerate for development
    compare_type=True,
    compare_server_default=True,
    # Include schema in comparisons
    include_schemas=True,
    # Render as batch for better compatibility
    render_as_batch=True,
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

if context.is_offline_mode():
    logger.info("🔄 Running migrations in offline mode")
    run_migrations_offline()
else:
    logger.info("🔄 Running migrations in online mode")
    run_migrations_online()

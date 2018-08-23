# This is a script that performs two functions.
#
# One is effectively a duplication of nova-manage api_db sync.
#
# Two is a more direct creation of placement database tables by
# direct reflection of the models, without migrations. This is
# good when we don't have existing data.
#
# Run it like the following get the second functionality, or don't
# set DB_CLEAN to get the first.
#
# DB_CLEAN=True python sync.py --config-file /etc/placement/placement.conf

import glob
import os
import sys

from migrate import exceptions
from migrate.versioning import api as versioning_api
from migrate.versioning.repository import Repository

from placement.api import wsgi
from placement.api import db_api
from placement import conf
from placement.db.sqlalchemy import api_models


# This needs to be updated to as new placement
# migrations are added.
PLACEMENT_MIGRATIONS = [
    '016_resource_providers.py',
    '026_add_resource_classes.py',
    '029_placement_aggregates.py',
    '041_resource_provider_traits.py',
    '043_placement_consumers.py',
    '044_placement_add_projects_users.py',
    '051_nested_resource_providers.py',
    '059_add_consumer_generation.py',
]


# The current tables used by placement
PLACEMENT_TABLES = [
    api_models.ResourceClass.__table__,
    api_models.ResourceProvider.__table__,
    api_models.ResourceProviderAggregate.__table__,
    api_models.PlacementAggregate.__table__,
    api_models.Inventory.__table__,
    api_models.Allocation.__table__,
    api_models.Trait.__table__,
    api_models.ResourceProviderTrait.__table__,
    api_models.Project.__table__,
    api_models.User.__table__,
    api_models.Consumer.__table__,
]


def _migration():
    # hack to the path of placement/db/sqlalchemy/migrate_repo/
    rel_path = os.path.join('placement', 'db', 'sqlalchemy', 'api_migrations',
                            'migrate_repo')
    path = os.path.join(os.path.abspath(os.path.dirname(conf.__file__)),
                        rel_path)
    # only use those migrations which actually do something for placement
    migration_dir_glob = os.path.join(path, 'versions', '*.py')
    for migration in glob.iglob(migration_dir_glob):
        if os.path.basename(migration) not in PLACEMENT_MIGRATIONS:
            with open(migration, 'w') as stopper:
                stopper.write('def upgrade(x): pass\n')

    repository = Repository(path)
    placement_engine = db_api.get_placement_engine()
    try:
        versioning_api.version_control(placement_engine, repository, None)
        return versioning_api.upgrade(
            db_api.get_placement_engine(), repository, None)
    except exceptions.DatabaseAlreadyControlledError as exc:
        sys.stderr.write('database probably already synced: %s\n' % exc)


def _create():
    """Create the placement tables fresh and new."""
    base = api_models.API_BASE
    engine = db_api.get_placement_engine()
    base.metadata.create_all(engine, tables=PLACEMENT_TABLES)
    sys.stderr.write('Created placement tables fresh\n')


if __name__ == '__main__':
    wsgi._parse_args(sys.argv, default_config_files=[])
    db_api.configure(conf.CONF)
    if os.environ.get('DB_CLEAN') == 'True':
        sys.stderr.write('creating database\n')
        _create()
    else:
        sys.stderr.write('migrating database\n')
        _migration()

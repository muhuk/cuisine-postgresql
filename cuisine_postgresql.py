try:
    from fabric.context_managers import cd, hide, settings
    from fabric.operations import sudo
    from fabric.utils import puts
    __fabric_available = True
except ImportError:
    __fabric_available = False


__version__ = '0.1.1'
__maintainer__ = u'Atamert \xd6l\xe7gen'
__email__ = 'muhuk@muhuk.com'
__all__ = [
    'postgresql_database_check',
    'postgresql_database_create',
    'postgresql_database_ensure',
    'postgresql_role_check',
    'postgresql_role_create',
    'postgresql_role_ensure',
]


def require_fabric(f):
    """
    Raises ``RuntimeError`` if the wrapped method is called but ``fabric``
    cannot be imported for some reason.
    """
    global __fabric_available
    if __fabric_available:
        return f
    else:
        def _f(*args, **kwargs):
            error_message = 'To use function "{0}", you must have ' \
                            'fabric in the import path'.format(f.func_name)
            raise RuntimeError(error_message)
        return _f


@require_fabric
def postgresql_database_check(database_name):
    cmd = 'psql -tAc "SELECT 1 FROM pg_database WHERE datname = \'{}\'"'
    with settings(hide('everything'), warn_only=True):
        return run_as_postgres(cmd.format(database_name)) == '1'


@require_fabric
def postgresql_database_create(database_name,
                               tablespace=None,
                               locale=None,
                               encoding=None,
                               owner=None,
                               template=None):
    opts = [
        tablespace and '--tablespace={0}'.format(tablespace),
        locale and '--locale={0}'.format(locale),
        encoding and '--encoding={0}'.format(encoding),
        owner and '--owner={0}'.format(owner),
        template and '--template={0}'.format(template),
    ]
    cmd = 'createdb -U postgres {opts} {database_name}'.format(
        opts=' '.join(opt for opt in opts if opt is not None),
        database_name=database_name,
    )
    run_as_postgres(cmd)


@require_fabric
def postgresql_database_ensure(database_name,
                               tablespace=None,
                               locale=None,
                               encoding=None,
                               owner=None,
                               template=None):
    if postgresql_database_check(database_name):
        puts('Database "{0}" exists.'.format(database_name))
    else:
        puts('Database "{0}" doesn\'t exist. Creating...'.format(database_name))
        postgresql_database_create(database_name,
                                   tablespace,
                                   locale,
                                   encoding,
                                   owner,
                                   template)


@require_fabric
def postgresql_role_check(username):
    cmd = 'psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = \'{}\'"'
    with settings(hide('everything'), warn_only=True):
        return run_as_postgres(cmd.format(username)) == '1'


@require_fabric
def postgresql_role_create(username,
                           password,
                           superuser=False,
                           createdb=False,
                           createrole=False,
                           inherit=True,
                           login=True):
    opts = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN'
    ]
    sql = 'CREATE ROLE {username} WITH {opts} PASSWORD \'{password}\''
    sql = sql.format(username=username, opts=' '.join(opts), password=password)
    cmd = 'psql -U postgres -c "{0}"'.format(sql)
    run_as_postgres(cmd)


@require_fabric
def postgresql_role_ensure(username,
                           password,
                           superuser=False,
                           createdb=False,
                           createrole=False,
                           inherit=True,
                           login=True):
    if postgresql_role_check(username):
        puts('Role "{0}" exists.'.format(username))
    else:
        puts('Role "{0}" doesn\'t exist. Creating...'.format(username))
        postgresql_role_create(username,
                               password,
                               superuser,
                               createdb,
                               createrole,
                               inherit,
                               login)


@require_fabric
def run_as_postgres(cmd):
    """
    Run given command as postgres user.
    """
    # The cd below is needed to avoid the following warning:
    #
    #     could not change directory to "/root"
    #
    with cd('/'):
        return sudo(cmd, user='postgres')

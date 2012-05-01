**cuisine-postgresql** provides cuisine-style PostgreSQL management commands.


Installation
============

::

    pip install cuisine-postgresql



Usage
=====


::

    from cuisine_postgresql import (postgresql_role_ensure,
                                    postgresql_database_ensure)


    @task
    def configure_database():
            postgresql_role_ensure('user', 'pass', createdb=True)
            postgresql_database_ensure('database',
                                       owner='user',
                                       template='template0',
                                       encoding='UTF8')

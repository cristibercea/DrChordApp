import os
from configparser import ConfigParser
from backend.domain.database.utils.DBException import DBException

def config(filename='database.ini', section='postgresql') -> dict[str, str | None]:
    """
    Configure PostgreSQL database using a certain section from a given .ini file.
    :param filename: the path of the .ini file; defaults to 'database.ini'
    :param section: the section in the .ini file; defaults to 'postgresql'
    :return: a dict of the database configuration
    :raises DBException: if the given section is not found
    :raises FileNotFoundError: if the given .ini file is not found
    """
    if os.path.isfile(filename):
        parser = ConfigParser()
        parser.read(filename)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params: db[param[0]] = param[1]
        else: raise DBException(f'Section {section} not found in the {filename} file!')
        return db
    raise FileNotFoundError(f'File {filename} not found!')
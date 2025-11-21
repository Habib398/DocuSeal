import satcfdi
import pkgutil
import sys

print(f'satcfdi path: {satcfdi.__file__}')
print(f'\nModulos de satcfdi:')

def list_modules(package, prefix=''):
    try:
        for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__+'.'):
            print(f'{prefix}{modname}')
    except Exception as e:
        print(f'Error: {e}')

list_modules(satcfdi)

from os.path import (
    basename,
    dirname,
    join
)
from glob import glob


from stdm.ui.forms import REG_EDITOR_CLS_EXTENSIONS


ext_dir = dirname(__file__)
for x in glob(join(ext_dir, '*.py')):
    if not x.endswith('__init__.py'):
        __import__(basename(x)[:-3], globals(), locals())

__all__ = ['REG_EDITOR_CLS_EXTENSIONS']

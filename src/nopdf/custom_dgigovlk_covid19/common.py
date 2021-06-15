"""Common utils."""
import logging

PROJECT_PREFIX = 'nopdf.dgigovlk'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('nopdf')


def _get_ref_prefix(ref_no):
    return '%s.ref%s' % (PROJECT_PREFIX, ref_no)

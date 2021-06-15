"""Common utils."""
import logging

log = logging.getLogger('nopdf')


def _get_ref_prefix(ref_no):
    return 'nopdf.dgigovlk.ref%s' % (ref_no)

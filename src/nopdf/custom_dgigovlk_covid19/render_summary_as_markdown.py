"""Render summary as markdown."""

from utils import filex

from nopdf.custom_dgigovlk_covid19.CONSTANTS import URL
from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log


def _get_details(data):
    details_lines = []
    if 'cum_conf' in data:
        details_lines.append(
            'Total cases: %d' % data['cum_conf'],
        )
    if 'new_conf' in data:
        details_lines.append(
            'New cases: %d' % data['new_conf'],
        )
    if 'cum_deaths' in data:
        details_lines.append(
            'Total deaths: %d' % data['cum_deaths'],
        )
    if 'new_deaths' in data:
        details_lines.append(
            'New deaths: %d' % data['new_deaths'],
        )
    return '. '.join(details_lines)


def render_summary_as_markdown(data_list):
    summary_file_name = '/tmp/README.md'
    lines = []
    lines.append('# Summary of COVID19 Press Releases')
    lines.append('Source: [Department of Government Information](%s)' % URL)

    for data in reversed(data_list):
        ref_no = data['ref_no']
        ref_prefix = _get_ref_prefix(ref_no)
        md_file = './%s.md' % (ref_prefix)

        lines.append('%s. [%s](%s)' % (
            ref_no,
            data['datetime'],
            md_file,
        ))

        details = _get_details(data)
        if details:
            lines.append('  * %s' % (
                details,
            ))

    filex.write(summary_file_name, '\n'.join(lines))
    log.info('Saved summary')

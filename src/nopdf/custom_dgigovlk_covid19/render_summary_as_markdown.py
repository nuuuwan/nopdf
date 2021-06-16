"""Render summary as markdown."""

from utils import filex

from nopdf.custom_dgigovlk_covid19.CONSTANTS import URL
from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log

MAX_UNCATEGORIZED_LINES = 140


def _get_details_lines(data):
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

    if 'released_from_isolation' in data:
        details_lines.append(
            'Some areas in districts %s released from isolation' % (
                ', '.join(list(map(
                    lambda area: area['district_name'],
                    data['released_from_isolation'],
                )))
            )
        )
    if not details_lines and 'uncategorized_text_lines' in data:
        uncat_lines = data['uncategorized_text_lines']
        details_lines.append(
            '\n'.join(uncat_lines)[:MAX_UNCATEGORIZED_LINES - 3] + '...',
        )

    return details_lines


def render_summary_as_markdown(data_list):
    summary_file_name = '/tmp/README.md'
    lines = []
    lines.append('# Summary of COVID19 Press Releases')
    lines.append('Source: [Department of Government Information](%s)' % URL)
    lines.append('\n')
    lines.append('\n')

    for data in reversed(data_list):
        ref_no = data['ref_no']
        ref_prefix = _get_ref_prefix(ref_no)
        md_file = './%s.md' % (ref_prefix)

        lines.append('%s. [%s](%s)' % (
            ref_no,
            data['datetime'],
            md_file,
        ))

        details_lines = _get_details_lines(data)
        if details_lines:
            lines.append('  * %s' % (
                '; '.join(details_lines),
            ))

    filex.write(summary_file_name, '\n'.join(lines))
    log.info('Saved summary')

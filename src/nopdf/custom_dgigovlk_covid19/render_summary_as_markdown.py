"""Render summary as markdown."""

from utils import filex

from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log


def render_summary_as_markdown(data_list):
    summary_file_name = '/tmp/README.md'
    lines = []
    lines.append('# Summary of COVID19 Press Releases')
    lines.append('Source: [Department of Government Information](%s)' % URL)

    for data in reversed(data_list):
        ref_no = data['ref_no']
        ref_prefix = _get_ref_prefix(ref_no)
        md_file = './%s.md' % (ref_prefix)

        lines.append('* [%s (%s)](%s)' % (
            data['datetime'],
            ref_no,
            md_file,
        ))
    filex.write(summary_file_name, '\n'.join(lines))
    log.info('Saved summary')

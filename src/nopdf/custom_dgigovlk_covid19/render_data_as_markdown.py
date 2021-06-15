"""Render data as markdown."""
import logging

from utils import filex

from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix


def render_data_as_markdown(data):
    """Render data as markdown."""
    ref_no = data['ref_no']

    rendered_time = ''
    if 'datetime' in data:
        rendered_time = '*%s*' % (data['datetime'])

    rendered_stats = ''
    if 'cum_conf' in data:
        rendered_stats += '* %s: %s\n' % (
            'Total Confirmed Cases',
            str(data['cum_conf']),
        )

    if 'cum_conf_new_year' in data:
        rendered_stats += '* %s: %s\n' % (
            'Total Confirmed Cases (New Year Cluster)',
            str(data['cum_conf_new_year']),
        )

    if 'cum_conf_patients' in data:
        rendered_stats += '* %s: %s\n' % (
            'Total Confirmed Cases (Not New Year Cluster)',
            str(data['cum_conf_patients']),
        )

    if 'new_conf' in data:
        rendered_stats += '* %s: %s\n' % (
            'New Cases',
            str(data['new_conf']),
        )
    if 'cum_deaths' in data:
        rendered_stats += '* %s: %s\n' % (
            'Total Deaths',
            str(data['cum_deaths']),
        )
    if 'deaths_by_day' in data:
        rendered_stats += '### Deaths by Day\n'
        for info in data['deaths_by_day']:
            rendered_stats += '* %s: %s\n' % (
                info['date'],
                str(info['deaths']),
            )
    if 'deaths_by_gender' in data:
        rendered_stats += '### Deaths by Gender\n'
        for info in data['deaths_by_gender']:
            rendered_stats += '* %s: %s\n' % (
                info['gender'],
                str(info['deaths']),
            )
    if 'deaths_by_age' in data:
        rendered_stats += '### Deaths by Age Group\n'
        for info in data['deaths_by_age']:
            rendered_stats += '* %s to %s: %s\n' % (
                str(info['age_range'][0]),
                str(info['age_range'][1]),
                str(info['deaths']),
            )

    if 'deaths_py_place' in data:
        rendered_stats += '### Deaths by Place\n'
        for info in data['deaths_py_place']:
            rendered_stats += '* %s: %s\n' % (
                info['place'],
                str(info['deaths']),
            )

    if 'areas_of_residence' in data:
        rendered_stats += '### Area of Residence of Fatalities\n'
        for area in data['areas_of_residence']:
            rendered_stats += '* %s\n' % (
                area,
            )
    if 'causes_of_death_lines' in data:
        rendered_stats += '### Cause of Death\n'
        for cause in data['causes_of_death_lines']:
            rendered_stats += '* %s\n' % (
                cause,
            )

    if rendered_stats:
        rendered_stats = '## Statistics\n%s' % (rendered_stats)

    rendered_rfi = ''
    if 'released_from_isolation' in data:
        rendered_rfi += '## Released from Isolation\n'
        for district in data['released_from_isolation']:
            rendered_rfi += '* %s District (%s) \n' % (
                district['district_name'],
                district['district_id'],
            )
            for police_area in district['police_areas']:
                rendered_rfi += '  * %s Police Area\n' % (
                    police_area['police_area_name'],
                )
                for area in police_area['areas']:
                    if 'area_name' in area:
                        rendered_rfi += '    * %s \n' % (
                            area['area_name'],
                        )
                    if 'gnd_name' in area:
                        rendered_rfi += '    * %s GND (%s) \n' % (
                            area['gnd_name'],
                            area['gnd_id'],
                        )

    render_uncategorized = ''
    if 'uncategorized_text_lines' in data:
        render_uncategorized += '...'
        if len(data['uncategorized_text_lines']) > 0:
            render_uncategorized = '\n'.join(
                list(map(
                    lambda line: '%s' % (line),
                    data['uncategorized_text_lines'],
                )),
            )

    ref_prefix = _get_ref_prefix(ref_no)
    md_file = '/tmp/%s.md' % (ref_prefix)
    filex.write(md_file, '''
# Press Release No. {ref_no}
{rendered_time}
{rendered_stats}
{rendered_rfi}
{render_uncategorized}
    '''.format(
        ref_no=ref_no,
        rendered_time=rendered_time,
        rendered_stats=rendered_stats,
        rendered_rfi=rendered_rfi,
        render_uncategorized=render_uncategorized,
    ))
    logging.debug('%s: Saved rendered data as markdown', ref_no)

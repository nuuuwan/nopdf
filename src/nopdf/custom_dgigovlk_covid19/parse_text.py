"""Parse text."""

import re
import datetime

from utils import timex
from gig import ents

from nopdf.custom_dgigovlk_covid19.IGNORE_REGEX_LIST import IGNORE_REGEX_LIST

from nopdf.custom_dgigovlk_covid19.constants_re import \
    REGEX_AGE_DEATHS, REGEX_CUM_CONF_NEW_YEAR, \
    REGEX_CUM_CONF_PATIENTS, REGEX_CUM_CONF, REGEX_CUM_DEATHS, \
    REGEX_DATE, REGEX_DAY_DEATHS, REGEX_GENDER_DEATHS, \
    REGEX_NEW_CONF, REGEX_PLACE_DEATHS, REGEX_TIME


def parse_text(ref_no, text):
    """Parse text."""
    lines = text.split('\n')

    info = {'ref_no': ref_no}

    deaths_by_day = []
    deaths_by_gender = []
    deaths_by_age = []
    deaths_py_place = []
    date_str = None
    time_str = None
    cum_conf = None
    cum_conf_new_year = None
    cum_conf_patients = None
    new_conf = None
    cum_deaths = None
    n_lines = len(lines)
    i_line = 0
    area_of_residence_lines = []
    cause_of_death_lines = []
    region_data = {}
    # region_data_in = {}
    region_data_out = {}
    district_name = None
    police_area_name = None
    uncategorized_text_lines = []

    while i_line < n_lines:
        line = lines[i_line].replace('¢', '').strip()
        i_line += 1
        if len(line.strip()) == 0:
            continue

        result = re.search(REGEX_TIME, line)
        if result:
            time_str = result.groupdict()['time']
            continue

        result = re.search(REGEX_DATE, line)
        if result:
            date_str = result.groupdict()['date']
            continue

        result = re.search(REGEX_CUM_CONF, line)
        if result:
            cum_conf = (int)(result.groupdict()['cum_conf'])
            continue

        result = re.search(REGEX_CUM_CONF_NEW_YEAR, line)
        if result:
            cum_conf_new_year = (int)(result.groupdict()['cum_conf_new_year'])
            continue

        result = re.search(REGEX_CUM_CONF_PATIENTS, line)
        if result:
            cum_conf_patients = (int)(result.groupdict()['cum_conf_patients'])
            continue

        result = re.search(REGEX_NEW_CONF, line)
        if result:
            new_conf = (int)(result.groupdict()['new_conf'])
            continue

        result = re.search(REGEX_CUM_DEATHS, line)
        if result:
            cum_deaths = (int)(result.groupdict()['cum_deaths'])
            continue

        result = re.search(REGEX_DAY_DEATHS, line)
        if result:
            result_data = result.groupdict()
            try:
                unixtime = timex.parse_time(
                    '2021 ' + result_data['day'],
                    '%Y %B %d',
                )
                date = datetime.datetime\
                    .fromtimestamp(unixtime)\
                    .strftime('%Y-%m-%d')
                deaths_by_day.append({
                    'unixtime': unixtime,
                    'date': date,
                    'deaths': (int)(result_data['deaths']),
                })
                continue
            except ValueError:
                pass

        result = re.search(REGEX_GENDER_DEATHS, line)
        if result:
            result_data = result.groupdict()
            deaths_by_gender.append({
                'gender': result_data['gender'],
                'deaths': (int)(result_data['deaths'])
            })
            continue

        result = re.search(REGEX_PLACE_DEATHS, line)
        if result:
            result_data = result.groupdict()
            deaths_py_place.append({
                'place': result_data['place'],
                'deaths': (int)(result_data['deaths'])
            })
            continue

        result = re.search(REGEX_AGE_DEATHS, line)
        if result:
            result_data = result.groupdict()
            age = result_data['age']
            if '-' in age:
                age_range = list(map(int, age.split('-')))
            elif '20' in age:
                age_range = [0, 20]
            else:
                age_range = [99, 130]
            deaths_by_age.append({
                'age_range': age_range,
                'deaths': (int)(result_data['deaths'])
            })
            continue

        if 'Area of Residence' in line:
            while True:
                line = lines[i_line]
                if len(line.strip()) > 0:
                    area_of_residence_lines.append(line)
                i_line += 1
                if '.' in line:
                    break
            continue

        if 'Causes of Death' in line:
            while True:
                line = lines[i_line]
                if len(line.strip()) > 0:
                    cause_of_death_lines.append(line)
                i_line += 1
                if '.' in line:
                    break
            continue

        if 'District' in line and len(line) < 25:
            district_name = line.replace('District', '').strip()
            if district_name not in region_data:
                region_data[district_name] = {}
            continue

        if 'Police Area' in line:
            police_area_name = line.replace('Police Area', '').strip()
            if police_area_name not in region_data[district_name]:
                region_data[district_name][police_area_name] = []
            continue

        if any([
            'Scheme' in line,
            'Place' in line,
            'Division' in line,
            'Diivision' in line,
            'Road' in line,
            'Mawatha' in line,
            'Grama' in line,
            'Complex' in line,
            'Estate' in line,
            'watta' in line,
        ]):
            gnd_name = line.replace('e ', '').replace('\u00a2', '')\
                .replace('© ', '').strip()
            gnd_name = gnd_name.replace('=', '').strip()
            if gnd_name in [
                'iladhari Diivision',
                'adhari Diivision',
                'iladhari Division',
                'iladhari Diivision',
                'ladhari Diivision',
                'iladhari Diivision',
            ]:
                continue
            if district_name and police_area_name:
                region_data[district_name][police_area_name].append(gnd_name)
            continue

        if 'released' in line:
            region_data = region_data_out
            continue

        # lines to ignore
        do_ignore = False
        for ignore_regex in IGNORE_REGEX_LIST:
            if re.search(ignore_regex, line):
                do_ignore = True
                break
            if len(line) < 10:
                do_ignore = True
                break
        if do_ignore:
            continue

        uncategorized_text_lines.append(line)

    info = {'ref_no': ref_no}
    if date_str:
        unixtime = timex.parse_time(
            date_str + ' ' + time_str.replace(':', '.'),
            '%d.%m.%Y' + ' ' + '%H.%M',
        )
        info['unixtime'] = unixtime
        info['datetime'] = datetime.datetime\
            .fromtimestamp(unixtime)\
            .strftime('%Y-%m-%d %H:%M')

    if cum_conf:
        info['cum_conf'] = cum_conf
    if cum_conf_new_year:
        info['cum_conf_new_year'] = cum_conf_new_year
    if cum_conf_patients:
        info['cum_conf_patients'] = cum_conf_patients
    if new_conf:
        info['new_conf'] = new_conf
    if cum_deaths:
        info['cum_deaths'] = cum_deaths

    if deaths_by_day:
        info['deaths_by_day'] = deaths_by_day
    if deaths_by_gender:
        info['deaths_by_gender'] = deaths_by_gender
    if deaths_by_age:
        info['deaths_by_age'] = sorted(
            deaths_by_age,
            key=lambda x: x['age_range'][0],
        )
    if deaths_py_place:
        info['deaths_py_place'] = deaths_py_place

    if area_of_residence_lines:
        info['areas_of_residence'] = sorted(
            ''.join(area_of_residence_lines).replace(', ', ',').split(',')
        )

    if cause_of_death_lines:
        info['causes_of_death_lines'] = sorted(
            ''.join(cause_of_death_lines).replace(', ', ',').split(',')
        )

    if region_data_out:
        region_data_out_formatted = []
        for district_name, district_data in sorted(
            region_data_out.items(),
            key=lambda item: item[0],
        ):

            districts = ents.get_entities_by_name_fuzzy(
                district_name,
                filter_entity_type='district',
            )
            district_id = ''
            if districts:
                district = districts[0]
                district_id = district['id']
                district_name = district['name']

            police_data_formatted = []
            for police_area_name, police_data in sorted(
                district_data.items(),
                key=lambda item: item[0],
            ):
                area_data_formatted = []

                for area in sorted(police_data):
                    gnds = ents.get_entities_by_name_fuzzy(
                        area.partition(' ')[0],
                        filter_entity_type='gnd',
                        filter_parent_id=district_id,
                    )
                    if gnds:
                        gnd = gnds[0]
                        area_data_formatted.append({
                            'gnd_id': gnd['id'],
                            'gnd_name': gnd['name'],
                        })
                    else:
                        area_data_formatted.append({
                            'area_name': area,
                        })

                police_data_formatted.append({
                    'police_area_name': police_area_name,
                    'areas': area_data_formatted,
                })

            region_data_out_formatted.append({
                'district_id': district_id,
                'district_name': district_name,
                'police_areas': police_data_formatted,
            })
        info['released_from_isolation'] = region_data_out_formatted

    if len(uncategorized_text_lines) > 0:
        info['uncategorized_text_lines'] = uncategorized_text_lines
    return info

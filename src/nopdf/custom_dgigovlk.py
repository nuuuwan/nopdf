"""CustomDgigovlk."""
import re
import json
import logging
import datetime

from utils import filex, www, timex, jsonx
from gig import ents

from nopdf import scrape, ocr

URL = 'https://www.dgi.gov.lk/news/press-releases-sri-lanka/covid-19-documents'

REGEX_MEDIA_URL = r'.+/(?P<date>\d{4}\.\d{2}\.\d{2})/.+' \
    + r'(?P<ref_no>\d{3}).+-page-(?P<page_no>\d{3}).+'
REGEX_TIME = r'Time\s*:\s*(?P<time>\d+.\d{2})\s*'
REGEX_DAY_DEATHS = r'(?P<day>\w+ \d{2})\s*-\s*(?P<deaths>\d+).*'
REGEX_GENDER_DEATHS = r'(?P<gender>\w+ale)\s*-\s*(?P<deaths>\d+).*'
REGEX_AGE_DEATHS = r'(?P<age>.+) [Y|y]ears\s*-\s*(?P<deaths>\d+).*'
REGEX_PLACE_DEATHS = r'(?P<place>.*(Residence|hospital).*)\s*-\s*(?P<deaths>\d+).*'

REGEX_DATE= r'(?P<date>\d{2}\.\d{2}\.\d{4})'
REGEX_CUM_CONFIRMED = r'Total - (?P<cum_confirmed>\d+)'
REGEX_NEW_CONFIRMED = r'\((?P<new_confirmed>\d+) within the day\)'
REGEX_CUM_DEATHS = r'.*total.*number.*COVID.*deaths.* (?P<cum_deaths>\d+)\s*'


def _get_fuzzy_fp(entity_name):
    fuzzy_fp = entity_name
    fuzzy_fp = fuzzy_fp.split(' ')[0]
    fuzzy_fp = fuzzy_fp.lower()
    fuzzy_fp = fuzzy_fp.replace("th", 't')
    fuzzy_fp = fuzzy_fp.replace("w", 'v')
    fuzzy_fp = fuzzy_fp[0] + re.sub('[aeiou]', '', fuzzy_fp[1:])
    return fuzzy_fp


entities_index = {
    'district': ents.get_entities('district'),
    'gnd': ents.get_entities('gnd'),
}


def _fuzzy_search_entity(entity_type, search_text, parent_id=''):
    entities = entities_index[entity_type]
    fp_search_text = _get_fuzzy_fp(search_text)
    for entity in entities:
        if parent_id not in entity['id']:
            continue
        fp_entity = _get_fuzzy_fp(entity['name'])

        if fp_entity == fp_search_text:
            return entity
    return None


def _parse_ref_text(ref_no, text):
    lines = text.split('\n')

    info = {
        'ref_no': ref_no,
    }

    deaths_by_day = []
    deaths_by_gender = []
    deaths_by_age = []
    deaths_py_place = []
    date_str = None
    time_str = None
    cum_confirmed = None
    new_confirmed = None
    cum_deaths = None
    n_lines = len(lines)
    i_line = 0
    area_of_residence_lines = []
    cause_of_death_lines = []
    region_data = None
    region_data_in = {}
    region_data_out = {}
    district_name = None
    police_area_name = None
    while (i_line < n_lines):
        line = lines[i_line]
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

        result = re.search(REGEX_CUM_CONFIRMED, line)
        if result:
            cum_confirmed = (int)(result.groupdict()['cum_confirmed'])
            continue

        result = re.search(REGEX_NEW_CONFIRMED, line)
        if result:
            new_confirmed = (int)(result.groupdict()['new_confirmed'])
            continue

        result = re.search(REGEX_CUM_DEATHS, line)
        if result:
            cum_deaths = (int)(result.groupdict()['cum_deaths'])
            continue

        result = re.search(REGEX_DAY_DEATHS, line)
        if result:
            result_data = result.groupdict()
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
            while(True):
                line = lines[i_line]
                if len(line.strip()) > 0:
                    area_of_residence_lines.append(line)
                i_line += 1
                if '.' in line:
                    break

        if 'Causes of Death' in line:
            while(True):
                line = lines[i_line]
                if len(line.strip()) > 0:
                    cause_of_death_lines.append(line)
                i_line += 1
                if '.' in line:
                    break

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
            'Road' in line,
            'Mawatha' in line,
        ]):
            gnd_name = line.replace('e ', '').replace('\u00a2', '').strip()
            if district_name and police_area_name:
                region_data[district_name][police_area_name].append(gnd_name)
            continue

        if 'released' in line:
            region_data = region_data_out

        print('- ', line)

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

    if cum_confirmed:
        info['cum_confirmed'] = cum_confirmed
    if new_confirmed:
        info['new_confirmed'] = new_confirmed
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

            district = _fuzzy_search_entity('district', district_name)
            district_id = ''
            if district:
                district_id = district['id']
                district_name = district['name']

            police_data_formatted = []
            for police_area_name, police_data in sorted(
                district_data.items(),
                key=lambda item: item[0],
            ):
                area_data_formatted = []

                for area in sorted(police_data):
                    gnd = _fuzzy_search_entity('gnd', area, district_id)
                    if gnd:
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

    return info


def _get_press_releases(url_list):

    def _is_press_release(url):
        return any([
            'Press_Release' in url,
            'PR_' in url,
        ])

    return list(filter(_is_press_release, url_list))


def custom_dgigovlk():
    """Run custom."""
    # get press release image urls
    media_url_list = scrape.scrape(URL)
    press_release_url_list = _get_press_releases(media_url_list)

    # group images by ref and page
    ref_to_page_to_url = {}
    for url in press_release_url_list:
        result = re.search(REGEX_MEDIA_URL, url)
        if not result:
            logging.error('Invalid URL format: %s', url)
            continue

        info = result.groupdict()
        ref_no = info['ref_no']
        page_no = info['page_no']

        if ref_no not in ref_to_page_to_url:
            ref_to_page_to_url[ref_no] = {}
        ref_to_page_to_url[ref_no][page_no] = url

    # extract text for each page, and collect
    for ref_no, page_to_url in sorted(
        ref_to_page_to_url.items(),
        key=lambda item: item[0],
    )[15:16]:
        # all_text = ''
        # for page_no, url in sorted(
        #     page_to_url.items(),
        #     key=lambda item: item[0],
        # ):
        #
        #     base_name = '/tmp/nopdf.dgigovlk.ref%s.page%s' % (
        #         ref_no,
        #         page_no,
        #     )
        #     text_file = '%s.txt' % (base_name)
        #     image_file = '%s.jpeg' % (base_name)
        #
        #     www.download_binary(url, image_file)
        #     text = ocr.ocr(image_file, text_file)
        #     # text = filex.read(text_file)
        #
        #     all_text += text

        base_name_all = '/tmp/nopdf.dgigovlk.ref%s' % (
            ref_no,
        )
        all_text_file = '%s.txt' % (base_name_all)
        # filex.write(all_text_file, all_text)
        all_text = filex.read(all_text_file)

        data = _parse_ref_text(ref_no, all_text)
        print('...')
        print(json.dumps(data, indent=2))
        data_file = '%s.json' % (base_name_all)
        jsonx.write(data_file, data)


if __name__ == '__main__':
    custom_dgigovlk()

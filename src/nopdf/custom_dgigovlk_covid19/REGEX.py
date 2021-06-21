"""Constants."""

REGEX_MEDIA_URL = r'.+/(?P<date>\d{4}\.\d{2}\.\d{2})/.+' \
    + r'(?P<ref_no>\d{3}).+-page-(?P<page_no>\d{3}).+'

REGEX_AGE_DEATHS = r'(?P<age>.+) [Y|y]ears\s*-\s*(?P<deaths>\d+).*'
REGEX_CUM_CONF = r'Total - (?P<cum_conf>\d+)'
REGEX_CUM_CONF_NEW_YEAR = r'.*New Year.* (?P<cum_conf_new_year>\d+)\s*'
REGEX_CUM_CONF_PATIENTS = r'.*atients reported.* (?P<cum_conf_patients>\d+)\s*'
REGEX_CUM_DEATHS = r'.*otal.*deaths.* (?P<cum_deaths>\d+)\s*'

REGEX_DATE = r'^(?P<date>\d{2}\.\d{2}\.\d{4})'
REGEX_DAY_DEATHS = r'(?P<day>[a-zA-Z]+ \d{2})\s*-\s*(?P<deaths>\d+).*'
REGEX_GENDER_DEATHS = r'(?P<gender>\w+ale)\s*-\s*(?P<deaths>\d+).*'
REGEX_NEW_CONF = r'\((?P<new_conf>\d+) within the day\)'
REGEX_PLACE_DEATHS = r'(?P<place>.*(Residence|hospital).*)\s*-' \
    + r'\s*(?P<deaths>\d+).*'
REGEX_GENDER_AGE_DEATHS = \
    r'^(?P<age>.+) (?P<male>(Ol|\dA,|-|\d{2})) (?P<female>(Ol|\dA,|-|\d{2})) (?P<total>(Ol|\dA,|-|\d{2}))'

REGEX_TIME = r'Time\s*:\s*(?P<time>\d+.\d{2})\s*'

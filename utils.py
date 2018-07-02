import datetime
import json
import xmlrpc.client

import pytz
import requests


BASE_URL = 'https://pypi.python.org/pypi'

DEPRECATED_PACKAGES = set((
    'distribute',
    'django-social-auth',
    'BeautifulSoup'
))

SESSION = requests.Session()


def req_rpc(method, *args):
    payload = xmlrpc.client.dumps(args, method)

    response = SESSION.post(
        BASE_URL,
        data=payload,
        headers={'Content-Type': 'text/xml'},
    )
    if response.status_code == 200:
        result = xmlrpc.client.loads(response.content)[0][0]
        return result
    else:
        # Some error occurred
        pass


def get_json_url(package_name):
    return BASE_URL + '/' + package_name + '/json'


def annotate_wheels(packages):
    print('Getting wheel data...')
    num_packages = len(packages)
    for index, package in enumerate(packages):
        print(index + 1, num_packages, package['name'])
        has_wheel = False
        is_universal = False
        url = get_json_url(package['name'])
        response = SESSION.get(url)
        if response.status_code != 200:
            print(' ! Skipping ' + package['name'])
            continue
        data = response.json()
        for download in data['urls']:
            if download['packagetype'] == 'bdist_wheel':
                has_wheel = True
            if has_wheel and 'none-any' in download['filename']:
                is_universal = True
        package['wheel'] = has_wheel
        package['universal'] = is_universal

        # Display logic. I know, I'm sorry.
        package['value'] = 1
        if has_wheel:
            package['css_class'] = 'success'
            package['icon'] = u'\u2713'  # Check mark
            package['title'] = 'This package provides a wheel.'
            if not is_universal:
                package['css_class'] = 'success_compiled'
                package['title'] = 'This package provides a platform specific wheel.'
        else:
            package['css_class'] = 'default'
            package['icon'] = u'\u2717'  # Ballot X
            package['title'] = ('This package has no wheel archives uploaded '
                                '(yet!).')


def get_top_packages():
    print('Getting packages...')
    packages = req_rpc('top_packages')
    return [{'name': n, 'downloads': d} for n, d in packages]


def not_deprecated(package):
    return package['name'] not in DEPRECATED_PACKAGES


def remove_irrelevant_packages(packages, limit):
    print('Removing cruft...')
    active_packages = list(filter(not_deprecated, packages))
    return active_packages[:limit]


def save_to_file(packages, file_name):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    with open(file_name, 'w') as f:
        f.write(json.dumps({
            'data': packages,
            'last_update': now.strftime('%A, %d %B %Y, %X %Z'),
        }))

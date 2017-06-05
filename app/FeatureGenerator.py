import csv, sys, time, os, re, urllib2, io
from bs4 import BeautifulSoup
import requests


def get_features_from_csv(input_file_name, output_file_name=None):
    '''Takes in path to csv file as input, writes to specified output file. If output
    file not provided, will prepend 'out_' to the input file.
    Goes to each url in the input file and determines the following features: 'url',
    'meeting-in-url', 'ratio-time', 'ratio-addr', 'count-days', 'count-meeting',
    'meeting-or-not'. Writes the features and the url to the output file as a csv.
    Returns number of successfully read urls.
    '''
    num_written = 0
    with open(input_file_name, 'rb') as input_csv:
        reader = csv.DictReader(input_csv)

        if output_file_name is None:
            output_file_name = 'out_' + input_file_name

        with open(output_file_name, 'w') as output_csv:
            fieldnames = ['url', 'meeting-in-url', 'ratio-time', 'ratio-addr',
                          'count-days', 'count-meeting', 'meeting-or-not']
            writer = csv.DictWriter(output_csv, fieldnames=(fieldnames))
            writer.writeheader()

            for input_row in reader:
                training = None
                if 'MeetingOrNot' in input_row.keys():
                    training = input_row['MeetingOrNot']
                elif 'meeting-or-not' in input_row.keys():
                    training = input_row['meeting-or-not']

                output_row = get_features_for_url(input_row['URL'], training)
                if output_row is None:
                    continue

                writer.writerow(output_row)
                num_written += 1

    return num_written


def get_features_for_url(url, is_meeting=None):
    ''' Gets the features 'meeting-in-url', 'ratio-time', 'ratio-addr', 'count-days',
    'count-meeting', 'meeting-or-not' for the specified url. If is_meeting is provided,
    will treat as training data and return as part of the features, if not, will write a
    '?' which is what WEKA uses to specify unknown.
    Does this by getting the counts for each feature, normalizing the features that need
    it and adding the above (meeting or not) to the final features. Returns the final
    features as a dict.
    '''
    parsed_data = __parse_webpage(url)
    if parsed_data is None:
        return None

    features = __parsed_data_to_features(parsed_data)
    if features is None:
        return None

    if is_meeting is None or type(is_meeting) != bool:
        features['meeting-or-not'] = '?'
    else:
        features['meeting-or-not'] = 1 if is_meeting else 0

    return features


def __parsed_data_to_features(parsed_data):
    ''' Takes in counts parsed from __parse_webpage and normalizes what needs to be
    normalized, returning a dict of the final features. If data is None, or length is
    <=0, returns None.
    '''
    if parsed_data is None:
        return None

    num_char = parsed_data['length']
    if num_char <= 0:
        return None

    return {
        'url': parsed_data['url'],
        'meeting-in-url': __meeting_in_url(parsed_data['url']),
        'ratio-time': float(parsed_data['times']) / num_char,
        'ratio-addr': float(parsed_data['addresses']) / num_char,
        'count-days': parsed_data['days'],
        'count-meeting': parsed_data['meetings'],
    }


def __get_webpage_fast(url):
    ''' This is slightly faster than __get_webpage_safe, but I think that it does not
    handle exceptions well. It is also less robust, so I recommend using
    __get_webpage_safe
    '''
    req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})

    try:
        response = urllib2.urlopen(req, timeout=3)
        web_content = response.read()
    except KeyboardInterrupt as e:
        raise KeyboardInterrupt
    except Exception as e:
        print "error: ", e, url
        return 0

    return response.geturl(), web_content


def __get_webpage_safe(url):
    ''' Slightly slower, but will return None instead of throwing an exception. Program
    can just skip the url rather than crashing. Also I think that the library is more
    reliable for determining success by using 'request.ok', i.e. it is more robist and
    will check more than I know how to manually as I did above in __get_webpage_fast.
    '''
    r = requests.get(url)
    if r.ok:
        return r.url, r.text
    return r.url, None


def __parse_webpage(url):
    ''' Goes to the url and tries to parse counts (not necessarily final features if
    normalized). If it does not get a successful response from the webpage, returns None.
    Else it strips the html tags, leaving just the text and passes to helper functions
    that extract counts from the page. Returns dictionary containing these counts if
    successful.
    '''
    url_retrieved, web_content = __get_webpage_safe(url)
    if web_content is None:
        return None

    soup = BeautifulSoup(web_content, 'html.parser')

    for script in soup(['script', 'style']):
        script.extract()

    text = soup.get_text().replace('\n', '')

    days = __count_days_in_text(text)
    addresses = __count_addresses_in_text(days['text_filtered'])
    times = __count_times_in_text(addresses['text_filtered'])

    return {
        'url': url_retrieved,
        'meetings': __count_meetings_in_text(text),
        'days': days['count'],
        'addresses': addresses['count'],
        'length': len(times['text_filtered']),
        'times': times['count'],
    }


def __count_times_in_text(text):
    text_filtered = text.lower()
    count = 0
    times = ['1 pm', '2 pm', '3 pm', '4 pm', '5 pm', '6 pm', '7 pm', '8 pm',
             '9 pm', '10 pm', '11 pm', '12 pm', '1 am', '2 am', '3 am', '4 am',
             '5 am', '6 am', '7 am', '8 am', '9 am', '10 am', '11 am', '12am',
             '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm',
             '10pm', '11pm', '12pm', '1am', '2am', '3am', '4am', '5am', '6am',
             '7am', '8am', '9am', '10am', '11am', '12am', '1p', '2p', '3p',
             '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p', '12p', '1a',
             '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a',
             '12a']

    time_regex = '\d{1,2}(:(\d{2})*)\s*(AM|am|PM|pm|a|p)'
    times_in_text = re.finditer(time_regex, text_filtered, re.I | re.M)
    text_filtered = re.sub(time_regex, '', text_filtered)

    for time in times_in_text:
        count += 1

    for time in times:
        if time in text_filtered:
            count = count + text_filtered.count(time)
            text_filtered = text_filtered.replace(time, '')

    return {'count': count, 'text_filtered': text_filtered}


def __count_addresses_in_text(text):
    text_filtered = text.lower()
    count = 0
    address_regex = ('\d{1,4} [\w\s\,\.]{0,20}(?:street|st|avenue|av|ave|road|'
                     'rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|'
                     'parkway|pkwy|circle|cir|boulevard|blvd)')

    addresses = re.finditer(address_regex, text_filtered, re.I | re.M)
    text_filtered = re.sub(address_regex, '', text_filtered)

    for address in addresses:
        count += 1

    count = count + text_filtered.count('church')
    text_filtered = text_filtered.replace('church', '')

    return {'count': count, 'text_filtered': text_filtered}


def __count_days_in_text(text):
    text_filtered = text.lower()
    count = 0
    days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

    for day in days:
        if day in text_filtered:
            count = count + text_filtered.count(day)
            text_filtered = text_filtered.replace(day, '')

    return {'count': count, 'text_filtered': text_filtered}


def __count_meetings_in_text(text):
    return text.lower().count('meeting')


def __meeting_in_url(url):
    return int('meeting' in url.lower())

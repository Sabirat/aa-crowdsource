import csv, sys, time, os, re, urllib2, io
from bs4 import BeautifulSoup


def get_features_from_csv(input_file_name, output_file_name=None):
  num_written = 0
  with open(input_file_name, 'rb') as input_csv:
    reader = csv.DictReader(input_csv)

    if output_file_name is None:
      output_file_name = 'out_' + input_file_name

    with open(output_file_name, 'w') as output_csv:
      fieldnames = ['URL', 'meeting-in-url', 'ratio-time', 'ratio-addr',
                    'count_days', 'count-meeting', 'meeting-or-not']
      writer = csv.DictWriter(outfile, fieldnames=(fieldnames))
      writer.writeHeader()

      for input_row in reader:
        training = None
        if 'MeetingOrNot' in input_row.keys():
          training = input_row['MeetingOrNot']
        elif 'meeting-or-not' in input_row.keys():
          training = input_row['meeting-or-not']

        output_row = get_features_for_url(input_row['URL'], training)
        if output_row == {}: continue

        writer.writerow(output_row)
        num_written += 1

  return num_written

def get_features_for_url(url, is_meeting = None):
  parsed_data = __parse_webpage(url)
  features = __parsed_data_to_features(parsed_data)

  if features == {}: return features

  if is_meeting is None or type(is_meeting) != bool:
    features['meeting-or-not'] = '?'
  else:
    features['meeting-or-not'] = 1 if is_meeting else 0

  return features

def __parsed_data_to_features(parsed_data):
  if parsed_data == 0: return {}

  num_char = parsed_data['length']
  if num_char <= 0: return {}

  return {
    'url': parsed_data['url'],
    'meeting-in-url': __meeting_in_url(parsed_data['url']),
    'ratio-time': float(parsed_data['times']) / num_char,
    'ratio-addr': float(parsed_data['addresses']) / num_char,
    'count-days': parsed_data['days'],
    'count-meeting': parsed_data['meetings'],
  }

def __parse_webpage(url):
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})

    try:
      response = urllib2.urlopen(req, timeout=3)
      web_content = response.read()
    except KeyboardInterrupt as e:
      raise KeyboardInterrupt
    except Exception as e:
      print "error: ", e, url
      return 0

    soup = BeautifulSoup(web_content, 'html.parser')

    for script in soup(['script', 'style']):
      script.extract()

    text = soup.get_text().replace('\n', '')

    days = __count_days_in_text(text)
    addresses = __count_addresses_in_text(days['text_filtered'])
    times = __count_times_in_text(addresses['text_filtered'])

    return {
      'url': url,
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
           '7am', '8am', '9am', '10am', '11am', '12am', '1p', '2p', '3p', '4p',
           '5p', '6p', '7p', '8p', '9p', '10p', '11p', '12p', '1a', '2a', '3a',
           '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12a']

  time_regex = '\d{1,2}(:(\d{2})*)\s*(AM|am|PM|pm|a|p)'
  times_in_text = re.finditer(time_regex, text_filtered, re.I | re.M)
  text_filtered = re.sub(time_regex, '', text_filtered)

  for time in times_in_text:
    count += 1

  for time in times:
    if time in text_filtered:
      count = count + text_filtered.count(time)
      text_filtered = text_filtered.replace(time, '')

  return { 'count': count, 'text_filtered': text_filtered }

def __count_addresses_in_text(text):
  text_filtered = text.lower()
  count = 0
  address_regex = ('\d{1,4} [\w\s\,\.]{0,20}(?:street|st|avenue|av|ave|road|rd|'
                   'highway|hwy|square|sq|trail|trl|drive|dr|court|ct|parkway|'
                   'pkwy|circle|cir|boulevard|blvd)')

  addresses = re.finditer(address_regex, text_filtered, re.I | re.M)
  text_filtered = re.sub(address_regex, '', text_filtered)

  for address in addresses:
    count += 1

  count = count + text_filtered.count('church')
  text_filtered = text_filtered.replace('church', '')

  return { 'count': count, 'text_filtered': text_filtered }

def __count_days_in_text(text):
  text_filtered = text.lower()
  count = 0
  days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
          'saturday','sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

  for day in days:
    if day in text_filtered:
      count = count + text_filtered.count(day)
      text_filtered = text_filtered.replace(day, '')

  return { 'count': count, 'text_filtered': text_filtered }

def __count_meetings_in_text(text):
  return text.lower().count('meeting')

def __meeting_in_url(url):
  return int('meeting' in url.lower())

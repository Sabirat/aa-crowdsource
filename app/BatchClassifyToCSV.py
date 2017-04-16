import csv, os, sys
from FeatureGenerator import get_features_from_csv
from ClassificationTools import (load_data_csv, prepare_data, classify_data,
                                 load_model, start_weka, stop_weka,
                                 crowdsource_data_split)


def main(argv):
    output_file = None
    if len(argv) > 1:
        output_file = argv[1]
    #get_features_directory(output_dir=output_file)
    classify_directory()


def get_features_directory(root_path='/Users/tommy/Desktop/States', output_dir=None):
    if output_dir is None:
        output_dir = './classify_out'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(root_path):
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext == '.csv':
                print name
                get_features_from_csv(os.path.join(root, file_name),
                                      os.path.join(output_dir, file_name))


def classify_directory(root_path='./classify_out'):
    start_weka()
    classifier = load_model('./my.model')
    # url classified(0,1) shouldbesent(0: no, 1: yes, 2: training)
    # meetingfromcw(int) nonmeetingfromvw(int) features
    for root, dirs, files in os.walk(root_path):
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext == '.csv':
                print file_name
                data = prepare_data(load_data_csv(os.path.join(root, file_name)))
                prediction_output = classify_data(data, classifier)
                crowdsource = crowdsource_data_split(prediction_output)
                temp_db_table(data=data, crowdsource=crowdsource, file_name=file_name)

    stop_weka()


def temp_db_table(data, crowdsource, file_name, output_dir='./temp_db'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.join(output_dir, file_name), 'w') as output_csv:
        features = dict(map(lambda a: list([a.name, a.index]), data.attributes()))
        fieldnames = features.keys() + ['crowdsource', 'meeting-cw', 'nonmeeting-cw']
        url_index = features.pop('url')

        writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(data.num_instances):
            instance = data.get_instance(i)
            url = instance.get_string_value(url_index)
            row = {'url': url}

            for feature, index in features.iteritems():
                row[feature] = instance.get_value(index)

            if url not in crowdsource:
                print 'url not found:', url
                continue

            row['crowdsource'] = crowdsource[url]['crowdsource']
            row['meeting-or-not'] = crowdsource[url]['meeting-page']
            row['meeting-cw'] = 0
            row['nonmeeting-cw'] = 0
            writer.writerow(row)
            

if __name__ == '__main__':
        main(sys.argv)

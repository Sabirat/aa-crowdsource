import csv, io, tempfile
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from weka.core.dataset import Attribute
from weka.core.converters import Loader, load_any_file
from weka.classifiers import Evaluation, PredictionOutput, FilteredClassifier, Classifier
from weka.filters import Filter


# TODO
def load_data_dict(features):
    ''' Turns dict of features into the 
    '''
    with tempfile.NamedTemporaryFile() as temp_csv:
        writer = csv.DictWriter(temp_csv.name, fieldnames=features.keys())


def load_data_csv(input_file_name):
    ''' Reads csv into the data object that weka likes and returns it. '''
    return load_any_file(input_file_name)


def prepare_data(data):
    ''' Converts boolean features from numeric to nominal, makes sure that we have all of
    the features that we want, 
    '''
    assert(data.attribute_by_name('meeting-or-not') is not None)
    assert(data.attribute_by_name('meeting-in-url') is not None)

    nominal_option_string = '{},{}'.format(
        data.attribute_by_name('meeting-or-not').index + 1,
        data.attribute_by_name('meeting-in-url').index + 1)

    num_to_nominal = Filter(
        classname='weka.filters.unsupervised.attribute.NumericToNominal',
        options=['-R', nominal_option_string])
    num_to_nominal.inputformat(data)
    data = num_to_nominal.filter(data)

    if not data.attribute_by_name('meeting-or-not').is_nominal:
        data.class_index = 0
        index_to_replace = data.attribute_by_name('meeting-or-not').index
        data.delete_attribute(index_to_replace)
        data.insert_attribute(Attribute.create_nominal('meeting-or-not', ['0', '1']),
                              index_to_replace)

    data.class_index = data.attribute_by_name('meeting-or-not').index

    # Features that are actually used in classification
    features_to_keep = ['url', 'meeting-in-url', 'ratio-time', 'ratio-addr',
                        'count-days', 'count-meeting', 'meeting-or-not']

    attributes = list(map(lambda attribute: attribute.name, data.attributes()))
    for feature in features_to_keep:
        assert(feature in attributes)

    delete_option_string = ''
    for attribute in data.attributes():
        if attribute.name not in features_to_keep:
            delete_option_string += (str(attribute.index + 1) + ',')

    remove_features = Filter(classname='weka.filters.unsupervised.attribute.Remove',
                             options=['-R', delete_option_string[:-1]])
    remove_features.inputformat(data)
    data = remove_features.filter(data)

    url_index = data.attribute_by_name('url').index
    reorder_option_string = str(url_index + 1) + ','
    for attribute in data.attributes():
        if attribute.index != url_index:
            reorder_option_string += (str(attribute.index + 1) + ',')

    move_url_to_front = Filter(classname='weka.filters.unsupervised.attribute.Reorder',
                               options=['-R', reorder_option_string[:-1]])
    move_url_to_front.inputformat(data)
    data = move_url_to_front.filter(data)

    return data


def create_classifier(data):
    classifier = Classifier(classname='weka.classifiers.meta.Bagging',
                            options=['-W', 'weka.classifiers.trees.RandomForest'])
    filtered_classifier = FilteredClassifier()

    remove_url = Filter(classname='weka.filters.unsupervised.attribute.Remove',
                        options=['-R', '1'])
    filtered_classifier.filter = remove_url
    filtered_classifier.classifier = classifier

    return filtered_classifier


def train_classifier(data, classifier):
    classifier.build_classifier(data)


def classify_data(data, classifier):
    remove_url = Filter(classname='weka.filters.unsupervised.attribute.Remove',
                        options=['-R', str(data.attribute_by_name('url').index + 1)])
    remove_url.inputformat(data)
    classifier.filter = remove_url

    evaluation = Evaluation(data)
    prediction_output = PredictionOutput(
        classname='weka.classifiers.evaluation.output.prediction.CSV',
        options=['-p', str(data.attribute_by_name('url').index + 1)])
    evaluation.test_model(classifier, data, prediction_output)

    return prediction_output


def save_model(classifier, output_file_name):
    serialization.write(output_file_name, classifier)


def load_model(input_file_name):
    return Classifier(jobject=serialization.read(input_file_name))


def crowdsource_data_split(prediction_output):
    csv_string = ('index,actual,predicted,error,prediction,url\n' +
                  prediction_output.buffer_content())

    predictions = csv.DictReader(csv_string.splitlines(),
                                 quotechar='\'')

    classified_data = {}

    for prediction in predictions:
        assert(prediction['predicted'] == '2:1' or prediction['predicted'] == '1:0')
        is_meeting = 1 if prediction['predicted'] == '2:1' else 0

        url = prediction['url'].replace('\\', '')
        classified_data[url] = {'meeting-page': is_meeting}

        if float(prediction['prediction']) >= 0.9:
            classified_data[url]['crowdsource'] = 0
        else:
            classified_data[url]['crowdsource'] = 1

    return classified_data


def start_weka():
    jvm.start()


def stop_weka():
    jvm.stop()

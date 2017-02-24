import csv, io, tempfile
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from weka.core.converters import Loader, load_any_file
from weka.classifiers import Evaluation, PredictionOutput, FilteredClassifier, Classifier
from weka.filters import Filter

'''
TODOS:
  [] make prepare_data generic for csv vs not csv
  [] make a csv specific function that does the other half of what prepare_data
     does now
  [] make function that takes single output from FeatureGenerator, converts to
     Instance datatype or whatever needed to pass into new prepare_data
'''


def load_data_dict(features):
  with tempfile.NamedTemporaryFile() as temp_csv:
    writer = csv.DictWriter(temp_csv.name, fieldnames=features.keys())
    print writer.header




def load_data_csv(input_file_name):
  return load_any_file(input_file_name)

def prepare_data(data):
  # Make nominal
  assert(data.attribute_by_name('meeting-or-not') is not None)
  assert(data.attribute_by_name('meeting-in-url') is not None)
  data.class_index = data.attribute_by_name('meeting-or-not').index

  nominal_option_string = '{},{}'.format(
      data.attribute_by_name('meeting-or-not').index + 1,
      data.attribute_by_name('meeting-in-url').index + 1)

  num_to_nominal = Filter(
      classname='weka.filters.unsupervised.attribute.NumericToNominal',
      options=['-R', nominal_option_string])

  num_to_nominal.inputformat(data)
  data = num_to_nominal.filter(data)

  # Features that are actually used in classification
  features_to_keep = ['meeting-in-url', 'ratio-time', 'ratio-addr',
                      'count-days', 'count-meeting', 'meeting-or-not']

  attributes = list(map(lambda attribute: attribute.name, data.attributes()))
  for feature in features_to_keep:
    assert(feature in attributes)

  delete_option_string = ''
  for attribute in data.attributes():
    if attribute.name not in features_to_keep:
      delete_option_string += (str(attribute.index + 1) + ',')

  remove_features = Filter(
      classname='weka.filters.unsupervised.attribute.Remove',
      options=['-R', delete_option_string[:-1]])

  classifier = Classifier(classname='weka.classifiers.meta.Bagging',
                          options=['-W', 'weka.classifiers.trees.RandomForest'])

  filtered_classifier = FilteredClassifier()
  filtered_classifier.filter = remove_features
  filtered_classifier.classifier = classifier
  filtered_classifier.build_classifier(data)

  return data, filtered_classifier

def classify_data(data, classifier):
  evaluation = Evaluation(data)
  prediction_output = PredictionOutput(
      classname='weka.classifiers.evaluation.output.prediction.CSV',
      options=['-p', str(data.attribute_by_name('url').index + 1)])
  evaluation.test_model(classifier, data, prediction_output)

  return prediction_output

def save_model(classifier, output_file_name):
  serialization.write(output_file_name, classifier)

def load_model(classifier, input_file_name):
  classifier = Classifier(jobject=serialization.read(input_file_name))

def crowdsource_data_split(prediction_output):
  csv_string = ('index,actual,predicted,error,probability,url\n' +
                prediction_output.buffer_content())
  predictions = csv.DictReader(csv_string.splitlines())
  classified_data = {}

  for prediction in predictions:
    assert(prediction['predicted'] == '2:1' or prediction['predicted'] == '1:0')
    is_meeting = 1 if prediction['predicted'] == '2:1' else 0
    classified_data[prediction['url']] = {'meeting_page': is_meeting}

    if float(prediction['probability']) >= 0.9:
      classified_data[prediction['url']]['crowdsource'] = 0
    else:
      classified_data[prediction['url']]['crowdsource'] = 1

  return classified_data

def start_weka():
  jvm.start()

def stop_weka():
  jvm.stop()

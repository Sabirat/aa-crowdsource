from ClassificationTools import load_data_dict, start_weka, stop_weka
from FeatureGenerator import get_features_for_url


def main():
  start_weka()

  features = get_features_for_url('http://www.aalakesumter.com/uploads/3/2/2/1/32210797/5099577_orig.jpg?250')

  load_data_dict(features)
  '''
  try:
    data, model = prepare_data('../combined.arff')
    crowds = crowdsource_data_split(classify_data(data, model))
  except Exception as e:
    print 'error: {}'.format(e)
  '''

  stop_weka()


if __name__ == '__main__':
  main()

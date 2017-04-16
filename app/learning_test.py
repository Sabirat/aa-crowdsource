from ClassificationTools import load_data_csv, start_weka, stop_weka, prepare_data, create_classifier, train_classifier, classify_data, save_model, load_model, crowdsource_data_split

from FeatureGenerator import get_features_for_url
def main():

    start_weka()



    test_csv = load_data_csv('./classify_out/test.csv')
    print 'num:', test_csv.num_instances
    test_data = prepare_data(test_csv)
    classifier_loaded = load_model('./my.model')
    pred_output = classify_data(test_data, classifier_loaded)
    crowdsource = crowdsource_data_split(pred_output)

    url_seen = set()

    url_index = test_data.attribute_by_name('url').index
    good = 0
    bad = 0
    for i in range(test_data.num_instances):
        instance = test_data.get_instance(i)
        url = instance.get_string_value(url_index)

        if url not in url_seen:
            url_seen.add(url)
        else:
            print 'dup:', url

        if url not in crowdsource:
            print 'url not found:', url
            continue

        if crowdsource[url]['crowdsource'] == 0:
            good += 1
        else:
            bad += 1


    print good, bad

    stop_weka()


if __name__ == '__main__':
    main()

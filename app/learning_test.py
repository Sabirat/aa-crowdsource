from ClassificationTools import load_data_csv, start_weka, stop_weka, prepare_data, create_classifier, train_classifier, classify_data, save_model, load_model, crowdsource_data_split

def main():
    start_weka()

    csv_data = load_data_csv('../combined.arff')

 # print csv_data.attribute_by_name('url').type
    data = prepare_data(csv_data)
    classifier = create_classifier(data)
    train_classifier(data, classifier)
    save_model(classifier, './my.model')


    test_csv = load_data_csv('./classify_out/test.csv')
    test_data = prepare_data(test_csv)
    classifier_loaded = load_model('./my.model')
    pred_output = classify_data(test_data, classifier_loaded)
    crowdsource = crowdsource_data_split(pred_output)


    c_num = 0
    ok_num = 0
    for url, data in crowdsource.iteritems():
            if data['crowdsource'] == 0:
                    ok_num += 1
            else:
                    c_num += 1

            #print data

    print c_num, ok_num



    stop_weka()


if __name__ == '__main__':
    main()

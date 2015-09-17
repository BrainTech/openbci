

from __future__ import print_function, division
from scipy.stats import wilcoxon
import pandas as pd

def count_average():
    """
    Function used to count average value 'pre' or 'post' (dual data contains
    two sets for each)
    """
    file_path = './data/markers_path_dual.csv'
    data = pd.read_csv(file_path, index_col=0, dtype='str')

    cols = ['stanie_zgodny', 'stanie_niezgodny',
            'bacznosc_zgodny', 'bacznosc_niezgodny',
            'gabka_zgodny', 'gabka_niezgodny']

    average_data = pd.DataFrame()
    average_data['username'] = pd.Series(data['username'])
    average_data['session_type'] = pd.Series(data['session_type'])
    for col in cols:
        average_col_pre = []
        average_col_post = []
        for row1, row2 in zip(data[col+'1_pre'].values, data[col+'2_pre'].values):
            if row1 == ' ' or row2 == ' ':
                average_col_pre.append(' ')
            else:
                average_col_pre.append((float(row1)+float(row2))/2)

        for row1, row2 in zip(data[col+'1_post'].values, data[col+'2_post'].values):
            if row1 == ' ' or row2 == ' ':
                average_col_pre[len(average_col_post)] = ' '
                average_col_post.append(' ')
            else:
                average_col_post.append((float(row1)+float(row2))/2)
        average_data['{}_{}'.format(col, 'pre')] \
            = pd.Series(average_col_pre, index=average_data.index)
        average_data['{}_{}'.format(col, 'post')] \
            = pd.Series(average_col_post, index=average_data.index)

    average_data.to_csv("./data/markers_path_dual_average.csv", sep=',')

def get_group_data(marker, test, version, group):
    file_path = './data/markers_dual_' + marker + '.csv'
    data = pd.read_csv(file_path, index_col=0, dtype='str')

    test_pre = test + '_' + version + '_pre'
    test_post = test + '_' + version + '_post'
    pre_str = data[data['session_type'] == group][test_pre].values
    post_str = data[data['session_type'] == group][test_post].values

    pre = []
    post = []
    for elem in pre_str:
        if elem is not ' ':
            elem = float(elem)
            pre.append(elem)
    for elem in post_str:
        if elem is not ' ':
            elem = float(elem)
            post.append(elem)

    return pre, post

def average_difference_sign(pre, post):
    sum = 0
    for i in range(0, len(pre)):
        sum += post[i] - pre[i]
    if sum/len(pre) == 0:
        return 0
    elif sum/len(pre) < 0:
        return '-'
    else:
        return '+'

def get_romberg():
    file_path = './data/markers_path_dual.csv'
    data = pd.read_csv(file_path, index_col=0, dtype='str')
    cols = ['bacznosc_', 'gabka_']
    versions = ['zgodny1_', 'niezgodny1_', 'zgodny2_', 'niezgodny2_']
    prefixes = ['pre', 'post']

    results = pd.DataFrame()
    results['username'] = pd.Series(data['username'])
    results['session_type'] = pd.Series(data['session_type'])

    for col in cols:
        for version in versions:
            for prefix in prefixes:
                romberg_col = []
                for row1, row2 in zip(data['stanie_'+version+prefix].values,
                                      data[col+version+prefix].values):
                    if row1 == ' ' or row2 == ' ':
                        romberg_col.append(' ')
                    else:
                        romberg_col.append(float(row1)/float(row2))
                results['{}{}{}'.format(col, version, prefix)] \
                    = pd.Series(romberg_col, index=results.index)

    results.to_csv("./data/markers_romberg_dual.csv", sep=',')

if __name__ == '__main__':
    # count_average()
    # get_romberg()

    markers = ['mean_x', 'mean_y', 'mean']
    tests = ['stanie', 'bacznosc', 'gabka']
    versions = ['zgodny', 'niezgodny']
    groups = ['cognitive', 'cognitive_motor', 'motor']

    analysis = pd.DataFrame()
    for marker in markers:
        for test in tests:
            if marker == 'romberg' and test == 'stanie':
                continue
            for version in versions:
                test_data = pd.DataFrame()
                test_data['marker'] = pd.Series(marker)
                test_data['test'] = pd.Series(test)
                test_data['version'] = pd.Series(version)
                for group in groups:
                    pre, post = get_group_data(marker, test, version, group)

                    test_data['{}_{}'.format('p_wilcoxon', group)] \
                        = pd.Series(wilcoxon(pre, post)[1])
                    test_data['{}_{}'.format('sign', group)] \
                        = pd.Series(average_difference_sign(pre, post))

                analysis = analysis.append(test_data)

    analysis.to_csv("./data/wilcoxon_dual_average.csv", sep=',')

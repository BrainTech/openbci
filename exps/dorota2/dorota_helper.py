#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@titanis.pl>
#
from acquisition import csv_manager
import random, os

def _get_control_rows(keys_map, count):
    colors = keys_map.keys()
    rows = []

    prev = colors[0]
    for i in range(count):
        tmp_colors = list(colors)
        tmp_colors.remove(prev)
        col = random.choice(tmp_colors)
        rows.append([col, col, keys_map[col], 1])
        prev = col

    return rows

def _get_experimental_rows(keys_map, count):
    colors = keys_map.keys()
    rows = []

    prev_text = colors[0]
    prev_col = colors[1]
    for i in range(count):
        tmp_colors = list(colors)
        tmp_colors.remove(prev_text)
        text_col = random.choice(tmp_colors)

        tmp_colors = list(tmp_colors)
        tmp_colors.remove(prev_col)
        try:
            tmp_colors.remove(text_col)
        except:
            pass

        col_col = random.choice(tmp_colors)

        rows.append([text_col, col_col, keys_map[col_col], 0])
        prev_text = text_col
        prev_col = col_col

    return rows

def generate_trials(file_name, conds_list, blocks_count,
                    trials_count, keys_map):
    file_name = os.path.expanduser(file_name)
    m = csv_manager.Writer(file_name, ',')
    m.write_row(["text","letterColor","corrAns","congruent"])
    for cond in conds_list:
        if cond == 'con':
            rows = _get_control_rows(keys_map, blocks_count*trials_count)
        elif cond == 'exp':
            rows = _get_experimental_rows(keys_map, blocks_count*trials_count)
        else:
            raise Excption("Unknown condition: "+str(cond))

        for row in rows:
            m.write_row(row)


    m.close()


if __name__ == '__main__':
    CONDITIONS = ['con', 'exp']
    CONDITIONS_COUNT = len(CONDITIONS)
    BLOCKS_COUNT = 4
    TRIALS_COUNT = 12
    KEYS_MAP = {'green':'7', 'red':'8', 'yellow':'9', 'blue':'0'}
    generate_trials('nic.csv', CONDITIONS, BLOCKS_COUNT, TRIALS_COUNT, KEYS_MAP)

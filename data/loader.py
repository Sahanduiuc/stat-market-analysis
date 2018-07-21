#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import pandas as pd

__author__ = 'maxim'


def load(filename):
  df = pd.read_csv(filename,
                   names=['ticker', 'period', 'date', 'time', 'open', 'high', 'low', 'close', 'vol'],
                   parse_dates={'timestamp': ['date', 'time']},
                   date_parser=lambda x: datetime.datetime.strptime(x, '%d/%m/%y %H:%M:%S'),
                   skiprows=1)

  return df


def main():
  plt.style.use('ggplot')
  pd.options.display.max_rows = 50
  pd.set_option('max_columns', 50)
  pd.set_option('max_colwidth', 50)
  pd.set_option('display.width', 200)

  df = load('.storage/SBER_2000-01-01_2018-07-21_day.txt')

  close_df = df[['timestamp', 'close']]
  close_df = close_df.set_index('timestamp')
  close_df = close_df.ix['2009-01-01':]
  close_df.plot()
  plt.show()


if __name__ == '__main__':
  main()

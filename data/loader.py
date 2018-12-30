#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import pandas as pd

__author__ = 'maxim'


def load(filename):
  df = pd.read_csv(filename,
                   names=['ticker', 'period', 'date', 'time', 'open', 'high', 'low', 'close', 'volume'],
                   parse_dates={'timestamp': ['date', 'time']},
                   date_parser=lambda x: datetime.datetime.strptime(x, '%d/%m/%y %H:%M:%S'),
                   skiprows=1)
  return df


def to_changes(raw):
  changes_df = pd.DataFrame(data={
    'timestamp': raw.timestamp,
    'high': raw.high.pct_change(),
    'low': raw.low.pct_change(),
    'open': raw.open.pct_change(),
    'close': raw.close.pct_change(),
    'volume': raw.volume.replace({0: 1e-5}).pct_change()
  }, columns=['timestamp', 'high', 'low', 'open', 'close', 'volume'])
  changes_df = changes_df.set_index('timestamp')
  changes_df = changes_df[1:]
  return changes_df


def return_series(raw, key='close', relative_to=None):
  name = '%s_return' % key
  if relative_to:
    returns = (raw[relative_to] - raw[key]) / raw[key]
  else:
    returns = raw[key].pct_change(1)
  return name, returns


def to_returns(raw, keys=('close',), relative_to=None):
  columns = {}
  for key in keys:
    name, series = return_series(raw, key=key, relative_to=relative_to)
    columns[name] = series
  returns_df = raw.assign(**columns)
  return returns_df


def main():
  df = load('.storage/SBER_2000-01-01_2018-07-21_day.txt')

  close_df = df[['timestamp', 'close']]
  close_df = close_df.set_index('timestamp')
  close_df = close_df.ix['2009-01-01':]
  close_df.plot(figsize=(10, 10))
  plt.show()

  changes = to_changes(df)
  changes = changes.ix['2009-01-01':]
  changes.plot(subplots=True, figsize=(10, 10))
  plt.show()


if __name__ == '__main__':
  plt.style.use('ggplot')
  pd.options.display.max_rows = 50
  pd.set_option('max_columns', 50)
  pd.set_option('max_colwidth', 50)
  pd.set_option('display.width', 200)

  main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'maxim'


import glob
import os
import pandas as pd

from data.fetcher import MAIN_EQUITIES
from data.loader import load, to_returns


STORAGE = '.storage'


def guess_path(ticker):
  mask = os.path.join(STORAGE, '%s_*_day.txt' % (ticker, ))
  matched = glob.glob(mask)
  assert matched, 'No files match the mask: %s' % mask
  return max(matched)


def get_returns(path, key='close'):
  price = load(path)
  price['timestamp'] = price['timestamp'].astype('datetime64[ns]')
  price = price.set_index('timestamp')
  df = to_returns(price, keys=[key])
  df = df.loc[:, ~df.columns.isin(['period'])]
  return df


def calc_sharpe(df, key='close_return'):
  returns = df[key]
  k = len(df) ** 0.5
  return returns.std(), returns.mean(), k * returns.mean() / returns.std()


def process(ticker):
  path = guess_path(ticker)
  df = get_returns(path)
  print(df.head())
  return calc_sharpe(df)


if __name__ == '__main__':
  all = []
  for ticker in MAIN_EQUITIES:
    values = process(ticker)
    all.append((ticker, ) + values)
  df = pd.DataFrame(all, columns=['ticker', 'std', 'mean', 'sharpe'])
  print(df)

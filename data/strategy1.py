#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'maxim'


"""
Predicting the day close/high price from the first hour.

Models: 
- when hour-close > hour-open
       hour-close < hour-open

Features:
- %(hour close), %(hour high)
- %(day open, prev day close)
- %(prev day close), %(prev day high)
"""

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

from data.loader import load, to_returns


def main():
  day_df = load('.storage/SBER_2000-01-01_2018-12-30_day.txt')
  day_rets = to_returns(day_df, keys=('high',))
  day_rets = day_rets.set_index('timestamp')
  day_rets = day_rets.ix['2012-01-01':]
  day_rets = day_rets[['high_return']]

  # Get first hour returns
  hour_df = load('.storage/SBER_2012-01-01_2018-07-29_hour.txt')
  hour_rets = to_returns(hour_df, keys=('close', 'high', 'low'))
  hour_rets = hour_rets.assign(day=pd.DatetimeIndex(hour_df.timestamp).normalize())
  hour_rets = hour_rets.drop_duplicates(subset='day')
  hour_rets = hour_rets.set_index('day')
  hour_rets = hour_rets[['close_return', 'high_return', 'low_return']]

  merged = hour_rets.join(day_rets, how='outer', lsuffix='_hour', rsuffix='_day')
  # plt.scatter(merged.close_return_hour, merged.close_return_day)
  # plt.show()

  print(merged.corr())

  x = hour_rets
  # x = sm.add_constant(x)
  y = day_rets
  model = sm.OLS(y, x).fit()
  print(model.summary())

  # from sklearn import linear_model
  # lm = linear_model.LinearRegression()
  # model = lm.fit(x, y)
  # print(lm.score(x, y))
  # print(lm.coef_, lm.intercept_)


if __name__ == '__main__':
  plt.style.use('ggplot')
  pd.options.display.max_rows = 50
  pd.set_option('max_columns', 50)
  pd.set_option('max_colwidth', 50)
  pd.set_option('display.width', 200)

  main()

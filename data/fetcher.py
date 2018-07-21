#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum
import os
import sys

from six.moves import urllib

__author__ = 'maxim'


def download_if_needed(url, path, filename=None):
  if not os.path.exists(path):
    os.makedirs(path)
  filename = filename or os.path.basename(url)
  full_path = os.path.join(path, filename)
  if not os.path.exists(full_path):
    print('Downloading %s, please wait...' % filename)
    result_path, _ = urllib.request.urlretrieve(url, full_path, _report_hook)
    stat = os.stat(result_path)
    print('Successfully downloaded "%s" (%d Kb)' % (filename, stat.st_size / 1024))
    return result_path
  else:
    print('Already downloaded:', full_path)
  return full_path


def _report_hook(block_num, block_size, total_size):
  read_so_far = block_num * block_size
  if total_size > 0:
    percent = read_so_far * 1e2 / total_size
    s = '\r%5.1f%% %*d / %d' % (percent, len(str(total_size)), read_so_far, total_size)
    sys.stdout.write(s)
    if read_so_far >= total_size:  # near the end
      sys.stdout.write('\n')
  else:  # total size is unknown
    sys.stdout.write('read %d\n' % (read_so_far,))


# Data source:
# http://www.finam.ru/profile/mosbirzha-fyuchersy/rts/export/
#
# Example:
# http://export.finam.ru/SBER_150101_180721.txt?market=1&em=3&code=SBER&apply=0&
#   df=1&mf=0&yf=2015&from=01.01.2015&dt=21&mt=6&yt=2018&to=21.07.2018&p=7&f=SBER_150101_180721&e=.txt&cn=SBER&
#   dtf=4&tmf=3&MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=1&at=1

URL_PATTERN = 'http://export.finam.ru/{name}{ext}?market=1&em=3&code={code}&apply=0&' \
              'df={from_day}&mf={from_month}&yf={from_year}&from={from_str}&' \
              'dt={to_day}&mt={to_month}&yt={to_year}&to={to_str}&' \
              'p={period}&f={name}&e={ext}&cn={code}&dtf={date_format}&tmf={time_format}&' \
              'MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=1&at=1'


class Period(Enum):
  TICK = 1
  MIN_1 = 2
  MIN_5 = 3
  MIN_10 = 4
  MIN_15 = 5
  MIN_30 = 6
  HOUR = 7
  DAY = 8
  WEEK = 9
  MONTH = 10

  def slug(self):
    name = self.name.lower()
    if '_' in name:
      before, after = name.split('_')
      return after + before
    return name


def generate_url(code, period, from_dt, to_dt):
  name = '%s_%s_%s_%s' % (code, from_dt.strftime('%Y-%m-%d'), to_dt.strftime('%Y-%m-%d'), period.slug())
  url = URL_PATTERN.format(
    name = name,
    ext = '.txt',
    code = code,

    from_day = from_dt.day,
    from_month = from_dt.month - 1,
    from_year = from_dt.year,
    from_str = from_dt.strftime('%d-%m-%Y'),

    to_day = to_dt.day,
    to_month = to_dt.month - 1,
    to_year = to_dt.year,
    to_str = to_dt.strftime('%d-%m-%Y'),

    period = period.value,

    date_format=4,
    time_format=3,
  )
  return url, '%s.txt' % name



def main():
  url, name = generate_url(code='SBER', period=Period.HOUR, from_dt=datetime(year=2015, month=1, day=1), to_dt=datetime.now())
  download_if_needed(url, path='.storage', filename=name)


if __name__ == '__main__':
  main()

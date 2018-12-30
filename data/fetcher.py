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

URL_PATTERN = 'http://export.finam.ru/{name}{ext}?market={market}&em={em}&code={code}&apply=0&' \
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


# Parsed from https://www.finam.ru/profile/mosbirzha-fyuchersy
class Market(Enum):
  MOEX_TOP = 200          # МосБиржа топ
  MOEX_STOCK = 1          # МосБиржа акции
  MOEX_FUTURES = 14       # МосБиржа фьючерсы
  MOEX_RUB = 41           # Курс рубля
  MOEX_FOREX = 45         # МосБиржа валютный рынок
  MOEX_BONDS = 2          # МосБиржа облигации
  MOEX_BONDS_OTHER = 12   # МосБиржа внесписочные облигации
  MOEX_OEF = 29           # МосБиржа пифы
  MOEX_ETF = 515          # Мосбиржа ETF
  NOTES = 8               # Расписки
  EUROBONDS = 519         # Еврооблигации
  SPBEX = 517             # Санкт-Петербургская биржа
  WORLD_IDX = 6           # Мировые Индексы
  COMMODITIES = 24        # Товары
  FOREX = 5               # Мировые валюты
  CRYPTO = 520            # Криптовалюты
  US_STOCK = 25           # Акции США(BATS)
  US_FUTURES = 7          # Фьючерсы США
  US_SECTORS = 27         # Отрасли экономики США
  US_TREASURIES = 26      # Гособлигации США
  ETF = 28                # ETF
  ECONOMY_IDX = 30        # Индексы мировой экономики
  RU_IDX = 91             # Российские индексы
  RTS = 3                 # РТС
  BOARD = 20              # Боард
  RTS_GAZ = 10            # РТС-GAZ
  ARCHIVE_FORTS = 17      # ФОРТС Архив
  ARCHIVE_COMMOD = 31     # Сырье Архив
  ARCHIVE_RTS_STD = 38    # RTS Standard Архив
  ARCHIVE_MMVB = 16       # ММВБ Архив
  ARCHIVE_RTS = 18        # РТС Архив
  ARCHIVE_SPBEX = 9       # СПФБ Архив
  ARCHIVE_RTS_BOARD = 32  # РТС-BOARD Архив
  ARCHIVE_NOTES = 39      # Расписки Архив
  ARCHIVE_SECTORS = -1    # Отрасли


def generate_url(code, em, period, from_dt, to_dt, market=Market.MOEX_STOCK):
  name = '%s_%s_%s_%s' % (code, from_dt.strftime('%Y-%m-%d'), to_dt.strftime('%Y-%m-%d'), period.slug())
  url = URL_PATTERN.format(
    name = name,
    ext = '.txt',
    code = code,
    em = em,
    market = market.value,

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


MOEX_EQUITIES = [
  {'name': u'МосЭнерго', 'code': '6', 'ticker': 'MSNG'},
  {'name': u'AGRO-гдр', 'code': '399716', 'ticker': 'AGRO'},
  {'name': u'ENPL-гдр', 'code': '489354', 'ticker': ''},
  {'name': u'FIVE-гдр', 'code': '491944', 'ticker': 'FIVE'},
  {'name': u'GTL ао', 'code': '152876', 'ticker': ''},
  {'name': u'Polymetal', 'code': '175924', 'ticker': 'POLY'},
  {'name': u'RUSAL plc', 'code': '414279', 'ticker': ''},
  {'name': u'Raven', 'code': '498713', 'ticker': ''},
  {'name': u'Yandex clA', 'code': '388383', 'ticker': 'YNDX'},
  {'name': u'iQIWI', 'code': '181610', 'ticker': 'QIWI'},
  {'name': u'iАвиастКао', 'code': '22843', 'ticker': ''},
  {'name': u'iДонскЗР', 'code': '74744', 'ticker': ''},
  {'name': u'iДонскЗР п', 'code': '74745', 'ticker': ''},
  {'name': u'iЗаводДИОД', 'code': '35363', 'ticker': ''},
  {'name': u'iИСКЧ ао', 'code': '17137', 'ticker': ''},
  {'name': u'iЛевенгук', 'code': '152517', 'ticker': ''},
  {'name': u'iНПОНаука', 'code': '81992', 'ticker': ''},
  {'name': u'iНаукаСвяз', 'code': '81929', 'ticker': ''},
  {'name': u'iРоллман', 'code': '152677', 'ticker': ''},
  {'name': u'iРоллман-п', 'code': '388313', 'ticker': ''},
  {'name': u'iФармсинтз', 'code': '74584', 'ticker': ''},
  {'name': u'АВТОВАЗ ао', 'code': '39', 'ticker': ''},
  {'name': u'АВТОВАЗ ап', 'code': '40', 'ticker': ''},
  {'name': u'АЛРОСА ао', 'code': '81820', 'ticker': 'ALRS'},
  {'name': u'АЛРОСА-Нюр', 'code': '81882', 'ticker': ''},
  {'name': u'АСКО ао', 'code': '484229', 'ticker': ''},
  {'name': u'АбрауДюрсо', 'code': '82460', 'ticker': ''},
  {'name': u'Авангрд-ао', 'code': '82843', 'ticker': ''},
  {'name': u'Акрон', 'code': '17564', 'ticker': ''},
  {'name': u'Аптеки36и6', 'code': '13855', 'ticker': ''},
  {'name': u'Армада', 'code': '19676', 'ticker': ''},
  {'name': u'Арсагера', 'code': '19915', 'ticker': ''},
  {'name': u'АстрЭнСб', 'code': '16452', 'ticker': ''},
  {'name': u'АшинскийМЗ', 'code': '20702', 'ticker': ''},
  {'name': u'Аэрофлот', 'code': '29', 'ticker': 'AFLT'},
  {'name': u'БСП ао', 'code': '20066', 'ticker': ''},
  {'name': u'БУДУЩЕЕ ао', 'code': '462599', 'ticker': ''},
  {'name': u'БашИнСв ао', 'code': '35242', 'ticker': ''},
  {'name': u'БашИнСв ап', 'code': '35243', 'ticker': ''},
  {'name': u'Башнефт ао', 'code': '81757', 'ticker': ''},
  {'name': u'Башнефт ап', 'code': '81758', 'ticker': ''},
  {'name': u'Белон ао', 'code': '21078', 'ticker': ''},
  {'name': u'Белуга ао', 'code': '19651', 'ticker': ''},
  {'name': u'БестЭфБ ао', 'code': '82616', 'ticker': ''},
  {'name': u'БурЗолото', 'code': '81901', 'ticker': ''},
  {'name': u'ВСМПО-АВСМ', 'code': '15965', 'ticker': ''},
  {'name': u'ВТБ ао', 'code': '19043', 'ticker': 'VTB'},
  {'name': u'ВТОРРЕСао', 'code': '82886', 'ticker': ''},
  {'name': u'ВХЗ-ао', 'code': '17257', 'ticker': ''},
  {'name': u'ВЭК 01 ао', 'code': '16352', 'ticker': ''},
  {'name': u'Варьеган', 'code': '81954', 'ticker': ''},
  {'name': u'Варьеган-п', 'code': '81955', 'ticker': ''},
  {'name': u'Возрожд-ао', 'code': '17068', 'ticker': ''},
  {'name': u'Возрожд-п', 'code': '17067', 'ticker': ''},
  {'name': u'ВолгЭнСб', 'code': '16456', 'ticker': ''},
  {'name': u'ВолгЭнСб-п', 'code': '16457', 'ticker': ''},
  {'name': u'ВыбСудЗ ао', 'code': '83251', 'ticker': ''},
  {'name': u'ВыбСудЗ ап', 'code': '83252', 'ticker': ''},
  {'name': u'ГАЗ ао', 'code': '81997', 'ticker': ''},
  {'name': u'ГАЗ ап', 'code': '81998', 'ticker': ''},
  {'name': u'ГАЗ-Тек ао', 'code': '82115', 'ticker': ''},
  {'name': u'ГАЗ-сервис', 'code': '81399', 'ticker': ''},
  {'name': u'ГАЗКОН-ао', 'code': '81398', 'ticker': ''},
  {'name': u'ГАЗПРОМ ао', 'code': '16842', 'ticker': 'GAZP'},
  {'name': u'ГЕОТЕК ао', 'code': '436120', 'ticker': ''},
  {'name': u'ГИТ ао', 'code': '449114', 'ticker': ''},
  {'name': u'ГМКНорНик', 'code': '795', 'ticker': 'GMNK'},
  {'name': u'ГТМ ао', 'code': '488918', 'ticker': ''},
  {'name': u'ГазпРнД ао', 'code': '152397', 'ticker': ''},
  {'name': u'Газпрнефть', 'code': '2', 'ticker': 'SIBN'},
  {'name': u'Галс-Девел', 'code': '17698', 'ticker': ''},
  {'name': u'ГлТоргПрод', 'code': '175842', 'ticker': ''},
  {'name': u'ДВМП ао', 'code': '20708', 'ticker': ''},
  {'name': u'ДЭК ао', 'code': '19724', 'ticker': ''},
  {'name': u'ДагСб ао', 'code': '16825', 'ticker': ''},
  {'name': u'ДетскийМир', 'code': '473181', 'ticker': ''},
  {'name': u'ЕТС ао', 'code': '419504', 'ticker': ''},
  {'name': u'ЕвроЭлтех', 'code': '487432', 'ticker': ''},
  {'name': u'ЗВЕЗДА ао', 'code': '82001', 'ticker': ''},
  {'name': u'ЗИЛ ао', 'code': '81918', 'ticker': ''},
  {'name': u'ИКРУСС-ИНВ', 'code': '81786', 'ticker': ''},
  {'name': u'ИНГРАД ао', 'code': '20711', 'ticker': ''},
  {'name': u'ИРКУТ-3', 'code': '15547', 'ticker': ''},
  {'name': u'ИСУ-КП', 'code': '386452', 'ticker': ''},
  {'name': u'Ижсталь ап', 'code': '81887', 'ticker': ''},
  {'name': u'Ижсталь2ао', 'code': '81885', 'ticker': ''},
  {'name': u'Инв-Девел', 'code': '409486', 'ticker': ''},
  {'name': u'ИнтерРАОао', 'code': '20516', 'ticker': ''},
  {'name': u'ИркЭнерго', 'code': '9', 'ticker': ''},
  {'name': u'КАМАЗ', 'code': '15544', 'ticker': ''},
  {'name': u'КЗМС ао', 'code': '17359', 'ticker': ''},
  {'name': u'КМЗ', 'code': '22525', 'ticker': ''},
  {'name': u'КСБ ао', 'code': '16284', 'ticker': ''},
  {'name': u'КСБ ап', 'code': '16285', 'ticker': ''},
  {'name': u'КУЗОЦМ ао', 'code': '81943', 'ticker': ''},
  {'name': u'КалужскСК', 'code': '16329', 'ticker': ''},
  {'name': u'КамчатЭ ао', 'code': '20030', 'ticker': ''},
  {'name': u'КамчатЭ ап', 'code': '20498', 'ticker': ''},
  {'name': u'Квадра', 'code': '18310', 'ticker': ''},
  {'name': u'Квадра-п', 'code': '18391', 'ticker': ''},
  {'name': u'Кокс ао', 'code': '75094', 'ticker': ''},
  {'name': u'КоршГОК ао', 'code': '20710', 'ticker': ''},
  {'name': u'КосогМЗ ао', 'code': '81903', 'ticker': ''},
  {'name': u'КрасОкт-1п', 'code': '511', 'ticker': ''},
  {'name': u'КрасОкт-ао', 'code': '510', 'ticker': ''},
  {'name': u'Красэсб ао', 'code': '20912', 'ticker': ''},
  {'name': u'Красэсб ап', 'code': '20913', 'ticker': ''},
  {'name': u'Кубанэнр', 'code': '522', 'ticker': ''},
  {'name': u'КузбТК ао', 'code': '35285', 'ticker': ''},
  {'name': u'КузнецкийБ', 'code': '83165', 'ticker': ''},
  {'name': u'Куйбазот', 'code': '81941', 'ticker': ''},
  {'name': u'Куйбазот-п', 'code': '81942', 'ticker': ''},
  {'name': u'КурганГКао', 'code': '83261', 'ticker': ''},
  {'name': u'КурганГКап', 'code': '152350', 'ticker': ''},
  {'name': u'ЛСР ао', 'code': '19736', 'ticker': ''},
  {'name': u'ЛУКОЙЛ', 'code': '8', 'ticker': 'LKOH'},
  {'name': u'ЛЭСК ао', 'code': '16276', 'ticker': ''},
  {'name': u'Лензол. ап', 'code': '22094', 'ticker': ''},
  {'name': u'Лензолото', 'code': '21004', 'ticker': ''},
  {'name': u'Лента др', 'code': '385792', 'ticker': ''},
  {'name': u'Ленэнерг-п', 'code': '542', 'ticker': ''},
  {'name': u'Ленэнерго', 'code': '31', 'ticker': 'LSGN'},
  {'name': u'М.видео', 'code': '19737', 'ticker': ''},
  {'name': u'МГТС-4ап', 'code': '12983', 'ticker': ''},
  {'name': u'МГТС-5ао', 'code': '12984', 'ticker': ''},
  {'name': u'МЕРИДИАН', 'code': '20947', 'ticker': ''},
  {'name': u'МКБ ао', 'code': '420694', 'ticker': ''},
  {'name': u'ММК', 'code': '16782', 'ticker': ''},
  {'name': u'МН-фонд ао', 'code': '80390', 'ticker': ''},
  {'name': u'МОЭСК', 'code': '16917', 'ticker': ''},
  {'name': u'МРСК СЗ', 'code': '20309', 'ticker': ''},
  {'name': u'МРСК СК', 'code': '20412', 'ticker': ''},
  {'name': u'МРСК Ур', 'code': '20402', 'ticker': ''},
  {'name': u'МРСК ЦП', 'code': '20107', 'ticker': 'MRKP'},
  {'name': u'МРСК Центр', 'code': '20235', 'ticker': ''},
  {'name': u'МРСКВол', 'code': '20286', 'ticker': ''},
  {'name': u'МРСКСиб', 'code': '20346', 'ticker': ''},
  {'name': u'МРСКЮга ао', 'code': '20681', 'ticker': ''},
  {'name': u'МТС-ао', 'code': '15523', 'ticker': 'MTS'},
  {'name': u'МагадЭн ао', 'code': '74562', 'ticker': ''},
  {'name': u'МагадЭн ап', 'code': '74563', 'ticker': ''},
  {'name': u'Магнит ао', 'code': '17086', 'ticker': 'MGNT'},
  {'name': u'МариЭнСб-п', 'code': '16331', 'ticker': ''},
  {'name': u'МегаФон ао', 'code': '152516', 'ticker': 'MFON'},
  {'name': u'Мегион-ао', 'code': '30', 'ticker': ''},
  {'name': u'Мегион-ап', 'code': '51', 'ticker': ''},
  {'name': u'МедиаВиМ', 'code': '81829', 'ticker': ''},
  {'name': u'Медиахолд', 'code': '20737', 'ticker': ''},
  {'name': u'Мечел ао', 'code': '21018', 'ticker': ''},
  {'name': u'Мечел ап', 'code': '80745', 'ticker': ''},
  {'name': u'МордЭнСб', 'code': '16359', 'ticker': ''},
  {'name': u'Морион ао', 'code': '81944', 'ticker': ''},
  {'name': u'МосБиржа', 'code': '152798', 'ticker': 'MOEX'},
  {'name': u'МосОблБанк', 'code': '82890', 'ticker': ''},
  {'name': u'Мостотрест', 'code': '74549', 'ticker': ''},
  {'name': u'МультиСис', 'code': '152676', 'ticker': ''},
  {'name': u'МурмТЭЦ-ао', 'code': '81945', 'ticker': ''},
  {'name': u'МурмТЭЦ-п', 'code': '81946', 'ticker': ''},
  {'name': u'НКНХ ао', 'code': '20100', 'ticker': ''},
  {'name': u'НКНХ ап', 'code': '20101', 'ticker': ''},
  {'name': u'НКХП ао', 'code': '450432', 'ticker': ''},
  {'name': u'НЛМК ао', 'code': '17046', 'ticker': ''},
  {'name': u'НМТП ао', 'code': '19629', 'ticker': ''},
  {'name': u'Нефтекамск', 'code': '81287', 'ticker': ''},
  {'name': u'Нижкамшина', 'code': '81947', 'ticker': ''},
  {'name': u'Новатэк ао', 'code': '17370', 'ticker': 'NVTK'},
  {'name': u'ОВК ао', 'code': '414560', 'ticker': ''},
  {'name': u'ОГК-2 ао', 'code': '18684', 'ticker': 'OGKB'},
  {'name': u'ОКС ао', 'code': '175781', 'ticker': ''},
  {'name': u'ОМЗ-ап', 'code': '15844', 'ticker': ''},
  {'name': u'ОР ао', 'code': '488674', 'ticker': ''},
  {'name': u'ОргСинт ао', 'code': '81856', 'ticker': ''},
  {'name': u'ОргСинт ап', 'code': '81857', 'ticker': ''},
  {'name': u'ПИК ао', 'code': '18654', 'ticker': ''},
  {'name': u'ПРОТЕК ао', 'code': '35247', 'ticker': ''},
  {'name': u'ПавлАвт ао', 'code': '81896', 'ticker': ''},
  {'name': u'ПермьЭнС-п', 'code': '16909', 'ticker': ''},
  {'name': u'ПермьЭнСб', 'code': '16908', 'ticker': ''},
  {'name': u'Плазмек', 'code': '81241', 'ticker': ''},
  {'name': u'Полюс', 'code': '17123', 'ticker': 'PLZL'},
  {'name': u'Приморье', 'code': '80818', 'ticker': ''},
  {'name': u'РБК ао', 'code': '74779', 'ticker': ''},
  {'name': u'РГС СК ао', 'code': '181934', 'ticker': ''},
  {'name': u'РДБанк ао', 'code': '181755', 'ticker': ''},
  {'name': u'РН-ЗапСиб', 'code': '81933', 'ticker': ''},
  {'name': u'РОСИНТЕРао', 'code': '20637', 'ticker': ''},
  {'name': u'Распадская', 'code': '17713', 'ticker': 'RASP'},
  {'name': u'Росбанк ао', 'code': '16866', 'ticker': ''},
  {'name': u'Роснефть', 'code': '17273', 'ticker': 'ROSN'},
  {'name': u'Россети ао', 'code': '20971', 'ticker': ''},
  {'name': u'Россети ап', 'code': '20972', 'ticker': ''},
  {'name': u'Ростел -ао', 'code': '7', 'ticker': 'RTKM'},
  {'name': u'Ростел -ап', 'code': '15', 'ticker': 'RTKMP'},
  {'name': u'РусАква ао', 'code': '35238', 'ticker': ''},
  {'name': u'РусГидро', 'code': '20266', 'ticker': 'HYDR'},
  {'name': u'Русгрэйн', 'code': '66893', 'ticker': ''},
  {'name': u'Русолово', 'code': '181316', 'ticker': ''},
  {'name': u'Русполимет', 'code': '20712', 'ticker': ''},
  {'name': u'РуссНфт ао', 'code': '465236', 'ticker': ''},
  {'name': u'РязЭнСб', 'code': '16455', 'ticker': ''},
  {'name': u'САФМАР ао', 'code': '491359', 'ticker': ''},
  {'name': u'СЗПароход', 'code': '22401', 'ticker': ''},
  {'name': u'СМЗ-ао', 'code': '20892', 'ticker': ''},
  {'name': u'СОЛЛЕРС', 'code': '16080', 'ticker': ''},
  {'name': u'СамарЭн-ао', 'code': '445', 'ticker': ''},
  {'name': u'СамарЭн-ап', 'code': '70', 'ticker': ''},
  {'name': u'СаратНПЗ', 'code': '81891', 'ticker': ''},
  {'name': u'СаратНПЗ-п', 'code': '81892', 'ticker': ''},
  {'name': u'СаратЭн-ао', 'code': '11', 'ticker': ''},
  {'name': u'СаратЭн-ап', 'code': '24', 'ticker': ''},
  {'name': u'Сахэнер ао', 'code': '473000', 'ticker': ''},
  {'name': u'Сбербанк', 'code': '3', 'ticker': 'SBER'},
  {'name': u'Сбербанк-п', 'code': '23', 'ticker': ''},
  {'name': u'СевСт-ао', 'code': '16136', 'ticker': 'CHMF'},
  {'name': u'Селигдар', 'code': '81360', 'ticker': ''},
  {'name': u'Селигдар-п', 'code': '82610', 'ticker': ''},
  {'name': u'СибГост ао', 'code': '436091', 'ticker': ''},
  {'name': u'Система ао', 'code': '19715', 'ticker': 'AFKS'},
  {'name': u'Слав-ЯНОСп', 'code': '15723', 'ticker': ''},
  {'name': u'Славн-ЯНОС', 'code': '15722', 'ticker': ''},
  {'name': u'СтаврЭнСб', 'code': '20087', 'ticker': ''},
  {'name': u'СтаврЭнСбп', 'code': '20088', 'ticker': ''},
  {'name': u'Сургнфгз', 'code': '4', 'ticker': ''},
  {'name': u'Сургнфгз-п', 'code': '13', 'ticker': ''},
  {'name': u'ТАНТАЛ ао', 'code': '81914', 'ticker': ''},
  {'name': u'ТАНТАЛ ап', 'code': '81915', 'ticker': ''},
  {'name': u'ТГК-1', 'code': '18382', 'ticker': ''},
  {'name': u'ТГК-14', 'code': '18176', 'ticker': ''},
  {'name': u'ТГК-2', 'code': '17597', 'ticker': ''},
  {'name': u'ТГК-2 ап', 'code': '18189', 'ticker': ''},
  {'name': u'ТЗА ао', 'code': '20716', 'ticker': ''},
  {'name': u'ТКЗ ао', 'code': '81899', 'ticker': ''},
  {'name': u'ТКЗКК ао', 'code': '81905', 'ticker': ''},
  {'name': u'ТКЗКК ап', 'code': '81906', 'ticker': ''},
  {'name': u'ТКСМ ао', 'code': '74746', 'ticker': ''},
  {'name': u'ТМК ао', 'code': '18441', 'ticker': ''},
  {'name': u'ТНСэКубань', 'code': '19916', 'ticker': ''},
  {'name': u'ТНСэнВор-п', 'code': '16547', 'ticker': ''},
  {'name': u'ТНСэнВорон', 'code': '16546', 'ticker': ''},
  {'name': u'ТНСэнМарЭл', 'code': '16330', 'ticker': ''},
  {'name': u'ТНСэнНН ао', 'code': '16615', 'ticker': ''},
  {'name': u'ТНСэнНН ап', 'code': '16616', 'ticker': ''},
  {'name': u'ТНСэнРст', 'code': '16783', 'ticker': ''},
  {'name': u'ТНСэнРст-п', 'code': '16784', 'ticker': ''},
  {'name': u'ТНСэнЯр', 'code': '16342', 'ticker': ''},
  {'name': u'ТНСэнЯр-п', 'code': '16343', 'ticker': ''},
  {'name': u'ТНСэнрг ао', 'code': '420644', 'ticker': ''},
  {'name': u'ТРК ао', 'code': '16797', 'ticker': ''},
  {'name': u'ТРК ап', 'code': '16798', 'ticker': ''},
  {'name': u'ТамбЭнСб', 'code': '16265', 'ticker': ''},
  {'name': u'ТамбЭнСб-п', 'code': '16266', 'ticker': ''},
  {'name': u'Татнфт 3ао', 'code': '825', 'ticker': ''},
  {'name': u'Татнфт 3ап', 'code': '826', 'ticker': ''},
  {'name': u'Таттел. ао', 'code': '18371', 'ticker': ''},
  {'name': u'Телеграф', 'code': '21002', 'ticker': ''},
  {'name': u'Телеграф-п', 'code': '81575', 'ticker': ''},
  {'name': u'ТрансК ао', 'code': '74561', 'ticker': ''},
  {'name': u'ТрансФ ао', 'code': '497210', 'ticker': ''},
  {'name': u'Транснф ап', 'code': '1012', 'ticker': ''},
  {'name': u'УрКузница', 'code': '82611', 'ticker': ''},
  {'name': u'УралСиб ао', 'code': '81953', 'ticker': ''},
  {'name': u'Уркалий-ао', 'code': '19623', 'ticker': ''},
  {'name': u'ФСК ЕЭС ао', 'code': '20509', 'ticker': 'FSK'},
  {'name': u'Физика ао', 'code': '81858', 'ticker': ''},
  {'name': u'ФосАгро ао', 'code': '81114', 'ticker': 'PHOR'},
  {'name': u'Химпром ао', 'code': '81939', 'ticker': ''},
  {'name': u'Химпром ап', 'code': '81940', 'ticker': ''},
  {'name': u'ЦМТ ао', 'code': '19095', 'ticker': ''},
  {'name': u'ЦМТ ап', 'code': '19096', 'ticker': ''},
  {'name': u'ЧЗПСН ао', 'code': '83121', 'ticker': ''},
  {'name': u'ЧКПЗ ао', 'code': '21000', 'ticker': ''},
  {'name': u'ЧМК ао', 'code': '21001', 'ticker': ''},
  {'name': u'ЧТПЗ ао', 'code': '20999', 'ticker': ''},
  {'name': u'ЧелябЭС ао', 'code': '16712', 'ticker': ''},
  {'name': u'ЧелябЭС ап', 'code': '16713', 'ticker': ''},
  {'name': u'ЧеркизГ-ао', 'code': '20125', 'ticker': ''},
  {'name': u'Электрцинк', 'code': '81934', 'ticker': ''},
  {'name': u'ЭнелРос ао', 'code': '16440', 'ticker': ''},
  {'name': u'ЭнергияРКК', 'code': '20321', 'ticker': ''},
  {'name': u'ЮТэйр ао', 'code': '15522', 'ticker': ''},
  {'name': u'ЮУНК ао', 'code': '82493', 'ticker': ''},
  {'name': u'ЮжКузб. ао', 'code': '20717', 'ticker': ''},
  {'name': u'Юнипро ао', 'code': '18584', 'ticker': ''},
  {'name': u'ЯТЭК ао', 'code': '81917', 'ticker': ''},
  {'name': u'Якутскэн-п', 'code': '81769', 'ticker': ''},
  {'name': u'Якутскэнрг', 'code': '81766', 'ticker': ''},
]

MOEX_CODES = {i['ticker']: i['code'] for i in MOEX_EQUITIES if i['ticker']}

MAIN_EQUITIES = [
  'AFLT', 'AGRO', 'ALRS', 'AFKS', 'CHMF', 'FIVE', 'FSK', 'GAZP', 'GMNK', 'HYDR', 'LKOH', 'LSGN',
  'MFON', 'MGNT', 'MSNG', 'MRKP',
  'MOEX', 'MTS', 'NVTK', 'OGKB', 'PHOR', 'PLZL', 'RASP', 'RTKM', 'SBER', 'SIBN', 'VTB', 'YNDX',
]


# Interesting periods:
#   url, name = generate_url(code='SBER', period=Period.DAY, from_dt=datetime(year=2000, month=1, day=1), to_dt=datetime.now())
#   url, name = generate_url(code='SBER', period=Period.HOUR, from_dt=datetime(year=2015, month=1, day=1), to_dt=datetime.now())
def main():
  for ticker in MAIN_EQUITIES:
    url, name = generate_url(code=ticker, em=MOEX_CODES[ticker],
                             period=Period.DAY,
                             from_dt=datetime(year=2000, month=1, day=1),
                             to_dt=datetime.now())
    download_if_needed(url, path='.storage', filename=name)


if __name__ == '__main__':
  main()

# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta

import pandas as pd
from dateutil import parser


def date_range(start_date,
               end_date=None,
               num=None,
               delta=None,
               mandatory_end_date=True,
               return_string_format=False,
               string_format='%Y-%m-%d'):
    """

    :param start_date: datetime or str (От даты)
    :param end_date: datetime or str (До даты)
    :param delta: int (интервал кол-во дней, между датами)
    :param return_string_format: bool (вернуть в даты в виду строки)
    :param string_format: str (формат выводимых дат в виде строки)
    :param mandatory_end_date: bool (сделать end_date конечной датой, если заданный интервал превысит её)
    :return: list
    """
    if type(start_date) is str:
        start_date = parser.parse(start_date)
    if type(end_date) is str:
        end_date = parser.parse(end_date)

    if type(delta) is int:
        delta = timedelta(delta)

    if not delta:
        return []
    if end_date and start_date > end_date:
        raise Exception("Wait. start_date needs to be before end_date")
    if end_date and num:
        raise Exception("Wait. Either specify end_date OR num")
    if not end_date and not num:
        end_date = datetime.now().date()

    l = []
    if end_date:
        while start_date <= end_date:
            l.append(start_date)
            start_date += delta
        if mandatory_end_date and end_date > l[-1]:
            # Если с выбранным интервалом конечная дата получается больше чем end_date, она не добавляеся,
            # поэтому добавляется end_date.
            l.append(end_date)
    else:
        for i in range(abs(num)):
            l.append(start_date)
            if num > 0:
                start_date += delta
            else:
                start_date -= delta

    if return_string_format:
        l = [i.strftime(string_format) for i in l]

    return sorted(l)


def period_range(start_date, end_date=None, num=None,
                 frequency='day', delta=1,
                 start_date_adjustment_by_frequency=True,
                 end_date_adjustment_by_frequency=False,
                 add_string_date=True,
                 return_type='dict', string_format='%Y-%m-%d'):
    """
    Генерирует интервалы дат по выбранной частоте.

    :param start_date:
    :param end_date:
    :param frequency: day | date | week | month | quarter | year ;
        Частота интервалов. Можно в разных регистрах указывать.
    :param start_date_adjustment_by_frequency: сделать началом периода выбранной частоты.
        Например если выбран месяц, то start_date будет переведен в дату начала месяца.
    :param return_type: 'dict' | 'tuple' ;
        dict вернет интервалы как [..., dict(date1=dt, date2=dt)]
        tuple вернет интервалы как [..., (dt, dt)]
    :param return_string_format: Если False вернет в формате datetime, иначе строкой
    :param string_format: формат возвращаемой строки, если return_string_format == True
    :return: [..., dict(date1=dt, date2=dt, date1_str=str, date2_str=str)] | [..., (dt, dt, str, str)]
    """
    if delta < 1:
        raise Exception('delta должна быть больше 0')

    frequency = frequency.lower()

    if type(start_date) is str:
        start_date = parser.parse(start_date)
    if type(end_date) is str:
        end_date = parser.parse(end_date)

    if end_date is None:
        if frequency in ('day', 'date'):
            end_date = start_date + timedelta(num - 1)
        else:
            # TODO: тест на вызов ошибки
            raise Exception('Определение end_date через num определено только для частоты day')

    if frequency in ('day', 'date'):
        first_date = start_date

        start_dates = []
        end_dates = []

        while first_date <= end_date:
            start_dates.append(first_date)
            end_dates.append((first_date + pd.offsets.Day(delta - 1)).to_pydatetime())

            first_date = (first_date + pd.offsets.Day(delta)).to_pydatetime()

    elif frequency == 'week':
        first_date = pd.Timestamp(start_date).to_period(freq='W').start_time.to_pydatetime()

        start_dates = []
        end_dates = []

        while first_date <= end_date:
            start_dates.append(first_date)
            end_dates.append((first_date + pd.offsets.Week(delta) - timedelta(1)).to_pydatetime())

            first_date = (first_date + pd.offsets.Week(delta)).to_pydatetime()

    elif frequency == 'month':
        first_date = pd.Timestamp(start_date).to_period(freq='M').start_time.to_pydatetime()

        start_dates = []
        end_dates = []

        while first_date <= end_date:
            start_dates.append(first_date)
            end_dates.append((first_date + pd.offsets.MonthEnd(delta)).to_pydatetime())

            first_date = (first_date + pd.offsets.MonthBegin(delta)).to_pydatetime()

    elif frequency == 'quarter':
        first_date = pd.Timestamp(start_date).to_period(freq='Q').start_time.to_pydatetime()

        start_dates = []
        end_dates = []

        while first_date <= end_date:
            start_dates.append(first_date)
            end_dates.append((first_date + pd.offsets.QuarterEnd(delta)).to_pydatetime())

            first_date = (first_date + pd.offsets.QuarterBegin(delta)).to_pydatetime()

    elif frequency == 'year':
        first_date = pd.Timestamp(start_date).to_period(freq='A').start_time.to_pydatetime()

        start_dates = []
        end_dates = []

        while first_date <= end_date:
            start_dates.append(first_date)
            end_dates.append((first_date + pd.offsets.YearEnd(delta)).to_pydatetime())

            first_date = (first_date + pd.offsets.YearBegin(delta)).to_pydatetime()

    else:
        raise Exception('Неизвестное значение frequence')

    if start_date_adjustment_by_frequency is False:
        # Дата начала frequence у start_date.
        start_dates[0] = start_date

    if end_date_adjustment_by_frequency is False:
        # last_date всегда превышает end_dates.
        end_dates[-1] = end_date

    if return_type == 'dict':
        dates = []
        for i, i2 in zip(start_dates, end_dates):
            date_ = dict(date1=i, date2=i2)
            if add_string_date:
                date_.update(date1_str=i.strftime(string_format),
                             date2_str=i2.strftime(string_format))
            dates.append(date_)

    elif return_type == 'tuple':
        dates = []
        for i, i2 in zip(start_dates, end_dates):
            if add_string_date:
                date_ = (i, i2, i.strftime(string_format), i2.strftime(string_format))
            else:
                date_ = (i, i2)
            dates.append(date_)
    else:
        raise Exception('Неверной значение в return_type допускается "dict" или "tuple"')

    return dates


def days_ago(days,
             from_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
             return_string=False,
             format='%Y-%m-%d'):
    if type(from_date) is str:
        from_date = parser.parse(from_date)

    dt = from_date - timedelta(days)

    return dt.strftime(format) if return_string else dt


def yesterday_date(return_string=False, format='%Y-%m-%d'):
    return days_ago(1, return_string=return_string, format=format)


def today_date(return_string=False, format='%Y-%m-%d'):
    return days_ago(0, return_string=return_string, format=format)
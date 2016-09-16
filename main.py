#！/usr/bin/env python3

"""Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets beijing shanghai 2016-08-25
"""
from docopt import docopt
from stations import stations
from pprint import pprint
from prettytable import PrettyTable
import requests

class TrainCollection(object):

    # 显示车次、出发/到达站、 出发/到达时间、历时、一等坐、二等坐、软卧、硬卧、硬座
    header = '车次 出发/到达站 出发/到达时间 时长 一等座 二等座 软卧 硬卧 硬座'.split()

    def __init__(self, rows):
        self.rows = rows

    def _get_duration(self, row):
        """
        获取车次运行时间
        """
        duration = row.get('lishi').replace(':', 'h') + 'm'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for row in self.rows:
            train = [
                # 车次
                row['station_train_code'],
                # 出发、到达站
                '\n'.join([row['from_station_name'], row['to_station_name']]),
                # 出发、到达时间
                '\n'.join([row['start_time'], row['arrive_time']]),
                # 历时
                self._get_duration(row),
                # 一等坐
                row['zy_num'],
                # 二等坐
                row['ze_num'],
                # 软卧
                row['rw_num'],
                # 软坐
                row['yw_num'],
                # 硬坐
                row['yz_num']
            ]
            yield train

    def pretty_print(self):
        """
        数据已经获取到了，剩下的就是提取我们要的信息并将它显示出来。
        `prettytable`这个库可以让我们它像MySQL数据库那样格式化显示数据。
        """
        pt = PrettyTable()
        # 设置每一列的标题
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


def cli():
    """command-line interface"""
    arguments = docopt(__doc__)
    print(arguments)
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']

    url = 'https://www.12306.cn/opn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(
        date, from_station, to_station
    )
    print(url)
    r = requests.get(url, verify = False)
    rows = r.json()['data']['datas']
    #pprint(rows, indent = 4)
    trains = TrainCollection(rows)
    trains.pretty_print()

if __name__ == '__main__':
    cli()
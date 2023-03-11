import datetime
import sys

def str2datetime(s):
    dte = datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    return dte

def print_failure(f):
    [address, start_datetime, end_datetime] = f
    print(f'故障サーバ: {address}, 故障期間: {start_datetime} ~ {end_datetime}')


# ある一つのサーバのlog（タプル）のリストを受け取る
# サーバアドレスと故障期間のタプル　のリストを返す
def check_failure_a_server(logs):
    #Pythonのリストの比較は最初の等価でない要素に対し行われる。ここでは時刻（になるはず）。
    sorted_logs = sorted(logs)

    isFailure = False
    failures = []

    for log in sorted_logs:
        [date, address, response] = log

        if isFailure:
            failures.append([address, t, str2datetime(date)])
            isFailure = False
        else:
            if log[2] == '-':
                t = str2datetime(log[0])
                isFailure = True

    #復旧のログがない場合
    if isFailure:
        failures.append([address, t, "現在"])
    
    return failures



def parse_logs_all(logs):

    addresses = []

    for log in logs:
        [date, address, response] = log

        if address not in addresses:
            addresses.append(address)


    failures = []
    # 各サーバごとにログを切り分け、それぞれでチェックしていく実装
    for address in addresses:
        logs_of_a_server = list(filter(lambda x: x[1] == address, logs))
        failures = check_failure_a_server(logs_of_a_server)
        for failure in failures:
            print_failure(failure)



def main(lines):

    # ＜確認日時＞,＜サーバアドレス＞,＜応答結果＞　を要素とするリストのリスト
    logs_all = list(map(lambda x: x.replace('\n', '').split(','), lines))

    parse_logs_all(logs_all)




if __name__ == '__main__':
    lines= open("log.txt", "r").readlines()
    main(lines)     
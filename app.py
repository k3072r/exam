import datetime
import sys

def str2datetime(s):
    dte = datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    return dte

def print_failure(failure_log):
    [address, start_datetime, end_datetime] = failure_log
    print(f'故障サーバ: {address}, 故障期間: {start_datetime} ~ {end_datetime}')

def print_overload(overload_log):
    [address, start_datetime, end_datetime] = overload_log
    print(f'過負荷サーバ: {address}, 過負荷期間: {start_datetime} ~ {end_datetime}')

# ある一つのサーバのlog（タプル）のリストを受け取る
# サーバアドレスと故障期間（開始時刻と終了時刻）のタプル　のリストを返す
def check_failure_a_server(logs, n):
    #Pythonのリストの比較は最初の等価でない要素に対し行われる。ここでは時刻（になるはず）。
    sorted_logs = sorted(logs)

    isFailure = 0
    failures = []

    for log in sorted_logs:
        [date, address, response] = log

        if response == '-':
            if isFailure == 0:
                t = str2datetime(date)  #故障開始時刻
            isFailure += 1
        else:
            if isFailure >= n:
                failures.append([address, t, str2datetime(date)])   #ここで復旧時刻を記録
            isFailure = 0

    #復旧のログがない場合
    if isFailure >= n:
        failures.append([address, t, "現在"])
    
    return failures


# ある一つのサーバのlog（タプル）のリストを受け取る
# サーバアドレスと過負荷期間（開始時刻と終了時刻）のタプル　のリストを返す
def check_overload_a_server(logs, m, t):
    sorted_logs = sorted(logs)

    count = 0
    sum = 0

    isOverload = False

    overloads = []

    for i, log in enumerate(sorted_logs):
        [date, address, response] = log

        if response == '-':
            count = 0
        else:
            sum += int(response)
            count += 1

            #直近で過負荷が起きているかチェック
            if count >= m:
                #ここまでで既に過負荷
                if isOverload:
                    #ここで過負荷じゃなくなる場合
                    if sum / count < t:
                        overloads.append([address, str2datetime(sorted_logs[i - count + 1][0]), str2datetime(date)])
                        isOverload = False
                    #まだ過負荷が続くなら何もしない（次に回す）

                #ここまでは過負荷でなかった
                else:
                    if sum / count >= t:
                        isOverload = True
    #end for
    
    #現在も過負荷の場合の処理
    if count >= m and sum / count >= t:
        overloads.append([address, str2datetime(sorted_logs[len(sorted_logs) - count][0]), "現在"])

    return overloads




def parse_logs_all(logs, n, m ,t):

    addresses = []

    for log in logs:
        [date, address, response] = log

        if address not in addresses:
            addresses.append(address)


    # 各サーバごとにログを切り分け、それぞれでチェックしていく実装
    for address in addresses:
        logs_of_a_server = list(filter(lambda x: x[1] == address, logs))

        failures = check_failure_a_server(logs_of_a_server, n)
        for failure in failures:
            print_failure(failure)

        overloads = check_overload_a_server(logs_of_a_server, m, t)
        for overload in overloads:
            print_overload(overload)




if __name__ == '__main__':
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    t = int(sys.argv[3])

    with open("log.txt", "r") as file:
        lines = file.readlines()
        # ＜確認日時＞,＜サーバアドレス＞,＜応答結果＞　を要素とするリストのリスト
        logs_all = list(map(lambda x: x.replace('\n', '').split(','), lines))
        parse_logs_all(logs_all, n, m, t)
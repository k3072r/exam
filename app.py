import datetime
import sys

def str2datetime(s):
    dte = datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    return dte

#サブネットは[192, 174, 25]のようなリストで保持し、そのリストのリストを返す
def get_subnet_list(failures):
    subnets = []
    for failure in failures:
        #一旦splitして比較（桁が違うかもなので）
        [address, t1, t2] = failure
        split_address = address.split('.')
        subnet = split_address[:3]
        if subnet not in subnets:
            subnets.append(subnet)
    #splitしたものをjoin
    subnets = list(map(lambda x: ".".join(x), subnets))
    return subnets

def get_address_list(logs):
    addresses = []
    for log in logs:
        [date, address, response] = log
        if address not in addresses:
            addresses.append(address)
    return addresses

def print_failure(failure_log):
    [address, start_datetime, end_datetime] = failure_log
    print(f'故障サーバ: {address}, 故障期間: {start_datetime} ~ {end_datetime}')

def print_overload(overload_log):
    [address, start_datetime, end_datetime] = overload_log
    print(f'過負荷サーバ: {address}, 過負荷期間: {start_datetime} ~ {end_datetime}')

def print_failure_subnet(failure_subnet_log):
    [subnet, start_datetime, end_datetime] = failure_subnet_log
    print(f'故障サブネット: {subnet}, 故障期間: {start_datetime} ~ {end_datetime}')



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


def check_failure_a_subnet(subnet, addresses, failures):
    matching_address = list(filter(lambda x: x[:len(subnet)] == subnet, addresses))
    
    #一つのサーバのfailureを取り出す
    failures_of_a_address = list(filter(lambda x: x[0] == matching_address[0], failures))
    failures_of_other_address = list(filter(lambda x: x[0] != matching_address[0], failures))

    failures_subnet = []

    for failure in failures_of_a_address:
        [address, start_time, end_time] = failure

        for failure2 in failures_of_other_address:
            [address2, start_time2, end_time2] = failure2
            
            failure_subnet = []
            if end_time == "現在":
                if start_time < start_time2:
                    failure_subnet = [subnet, start_time, end_time2]
                elif end_time2 != "現在" and start_time < end_time2:
                    failure_subnet = [subnet, end_time2, end_time]
            else:
                if end_time2 == "現在":
                    if start_time2 < end_time:
                        failure_subnet = [subnet, end_time, end_time2]
                else:
                    common_start = max(start_time, start_time2)
                    common_end = min(end_time, end_time2)
                    if common_start <= common_end:
                        failure_subnet = [subnet, common_start, common_end]
            
            #共通範囲が存在する場合
            if failure_subnet != []:
                failures_subnet.append(failure_subnet)

    return failures_subnet




def parse_logs_all(logs, n, m ,t):

    addresses = get_address_list(logs)

    all_failures = []

    # 各サーバごとにログを切り分け、それぞれでチェックしていく実装
    for address in addresses:
        logs_of_a_server = list(filter(lambda x: x[1] == address, logs))

        failures = check_failure_a_server(logs_of_a_server, n)
        for failure in failures:
            print_failure(failure)
            all_failures.append(failure)

        overloads = check_overload_a_server(logs_of_a_server, m, t)
        for overload in overloads:
            print_overload(overload)

    subnets = get_subnet_list(all_failures)
    for subnet in subnets:
        failures_subnet = check_failure_a_subnet(subnet, addresses, all_failures)
        for failure_subnet in failures_subnet:
            print_failure_subnet(failure_subnet)



if __name__ == '__main__':
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    t = int(sys.argv[3])

    with open("log.txt", "r") as file:
        lines = file.readlines()
        # ＜確認日時＞,＜サーバアドレス＞,＜応答結果＞　を要素とするリストのリスト
        logs_all = list(map(lambda x: x.replace('\n', '').split(','), lines))
        parse_logs_all(logs_all, n, m, t)
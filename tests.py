from test.support import captured_stdout
import sys
sys.path.append('../')
from app import parse_logs_all
import unittest

class BaseTestCase(unittest.TestCase):

    def template(self, test_logs, n, m, t, ans):

        test_logs = test_logs.split('\n')
        test_logs = [log for log in test_logs if log != '']
        test_logs = list(map(lambda x: x.strip().split(','), test_logs))

        ans = ans.split('\n')
        ans = [e for e in ans if e != '']
        ans = list(map(lambda x: x.strip(), ans))

        with captured_stdout() as stdout:
            parse_logs_all(test_logs, n, m, t)
            lines = stdout.getvalue().splitlines()

        for i, line in enumerate(lines):
            self.assertEqual(line, ans[i])



    def test1(self):
        #故障（-）を検知できる
        test_logs = """
        20201019133124,10.20.30.1/16,2
        20201019133125,10.20.30.2/16,1
        20201019133134,192.168.1.1/24,10
        20201019133135,192.168.1.2/24,5
        20201019133224,10.20.30.1/16,522
        20201019133225,10.20.30.2/16,1
        20201019133234,192.168.1.1/24,8
        20201019133235,192.168.1.2/24,15
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,2"""
        n = 1
        m = 1
        t = 1000
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 現在"""
        self.template(test_logs, n, m, t, ans)

    def test2(self):
        #故障（-）と復旧を検知できる
        test_logs = """
        20201019133234,192.168.1.1/24,8
        20201019133235,192.168.1.2/24,15
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,2
        20201019133424,10.20.30.1/16,1"""
        n = 1
        m = 1
        t = 1000
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:34:24"""
        self.template(test_logs, n, m, t, ans)

    def test3(self):
        #複数の故障を検知できる
        test_logs = """
        20201019133224,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,-
        20201019133226,10.20.30.1/16,1"""
        n = 1
        m = 1
        t = 1000
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:32:24 ~ 2020-10-19 13:32:26
        故障サーバ: 10.20.30.2/16, 故障期間: 2020-10-19 13:33:25 ~ 現在"""
        self.template(test_logs, n, m, t, ans)

    def test4(self):
        #複数のログにまたがる故障を検知できる
        test_logs = """
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,2
        20201019133424,10.20.30.1/16,-
        20201019133524,10.20.30.1/16,-
        20201019133624,10.20.30.1/16,1"""
        n = 1
        m = 1
        t = 1000
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:36:24"""
        self.template(test_logs, n, m, t, ans)

    def test5(self):
        #n > 1の場合に故障を検知できる・途中で復旧した場合に検知しない
        test_logs = """
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,-
        20201019133424,10.20.30.1/16,-
        20201019133524,10.20.30.1/16,-
        20201019133326,10.20.30.2/16,2
        20201019133624,10.20.30.1/16,1"""
        n = 2
        m = 1
        t = 1000
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:36:24"""
        self.template(test_logs, n, m, t, ans)

    def test6(self):
        #（故障・）過負荷を検知できる
        test_logs = """
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,-
        20201019133235,192.168.1.2/24,15
        20201019133424,10.20.30.1/16,-
        20201019133524,10.20.30.1/16,-
        20201019133326,10.20.30.2/16,1
        20201019133624,10.20.30.1/16,0
        20201019133327,10.20.30.2/16,0"""
        n = 2
        m = 1
        t = 1
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:36:24
        過負荷サーバ: 10.20.30.2/16, 過負荷期間: 2020-10-19 13:33:26 ~ 2020-10-19 13:33:27
        過負荷サーバ: 192.168.1.2/24, 過負荷期間: 2020-10-19 13:32:35 ~ 現在"""
        self.template(test_logs, n, m, t, ans)

    def test7(self):
        #過負荷中に故障した場合に過負荷としては検知しない
        test_logs = """
        20201019133324,10.20.30.1/16,500
        20201019133235,192.168.1.2/24,15
        20201019133424,10.20.30.1/16,500
        20201019133524,10.20.30.1/16,-
        20201019133624,10.20.30.1/16,0"""
        n = 2
        m = 3
        t = 1
        ans = """過負荷サーバ: 192.168.1.2/24, 過負荷期間: 2020-10-19 13:32:35 ~ 現在"""
        self.template(test_logs, n, m, t, ans)

    def test8(self):
        #長期間の過負荷を正しく出力できる
        test_logs = """
        20201019133224,10.20.30.1/16,0
        20201019133324,10.20.30.1/16,500
        20201019133424,10.20.30.1/16,500
        20201019133524,10.20.30.1/16,500
        20201019133624,10.20.30.1/16,500
        20201019133724,10.20.30.1/16,500
        20201019133824,10.20.30.1/16,0"""
        n = 1
        m = 3
        t = 500
        ans = """過負荷サーバ: 10.20.30.1/16, 過負荷期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:38:24"""
        self.template(test_logs, n, m, t, ans)

    def test9(self):
        #ログの順番がバラバラでも正しく動作する
        test_logs = """
        20201019133724,10.20.30.1/16,500
        20201019133524,10.20.30.1/16,500
        20201019133324,10.20.30.1/16,500
        20201019133424,10.20.30.1/16,500
        20201019133824,10.20.30.1/16,0
        20201019133624,10.20.30.1/16,500"""
        n = 1
        m = 3
        t = 500
        ans = """過負荷サーバ: 10.20.30.1/16, 過負荷期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:38:24"""
        self.template(test_logs, n, m, t, ans)

    def test10(self):
        #サブネットの故障を検知できる
        test_logs = """
        20201019133324,10.20.30.1/16,-
        20201019133325,10.20.30.2/16,-
        20201019133235,192.168.1.2/24,15
        20201019133424,10.20.30.1/16,-
        20201019133524,10.20.30.1/16,-
        20201019133326,10.20.30.2/16,1
        20201019133624,10.20.30.1/16,1
        20201019133327,10.20.30.2/16,0"""
        n = 1
        m = 1
        t = 10
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 2020-10-19 13:36:24
        故障サーバ: 10.20.30.2/16, 故障期間: 2020-10-19 13:33:25 ~ 2020-10-19 13:33:26
        過負荷サーバ: 192.168.1.2/24, 過負荷期間: 2020-10-19 13:32:35 ~ 現在
        故障サブネット: 10.20.30, 故障期間: 2020-10-19 13:33:25 ~ 2020-10-19 13:33:26"""
        self.template(test_logs, n, m, t, ans)

    def test11(self):
        #サーバの故障期間が被らない場合はサブネットの故障としない
        test_logs = """
        20201019133324,10.20.30.1/16,-
        20201019133125,10.20.30.2/16,-
        20201019133235,192.168.1.2/24,15
        20201019133424,10.20.30.1/16,-
        20201019133524,10.20.30.1/16,-
        20201019133226,10.20.30.2/16,1"""
        n = 1
        m = 1
        t = 10
        ans = """故障サーバ: 10.20.30.1/16, 故障期間: 2020-10-19 13:33:24 ~ 現在
        故障サーバ: 10.20.30.2/16, 故障期間: 2020-10-19 13:31:25 ~ 2020-10-19 13:32:26
        過負荷サーバ: 192.168.1.2/24, 過負荷期間: 2020-10-19 13:32:35 ~ 現在"""
        self.template(test_logs, n, m, t, ans)

if __name__ == "__main__":
    unittest.main()
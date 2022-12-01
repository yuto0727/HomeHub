import mmap
import os
from time import sleep

class mmap_global_val:
    """
    file_name: 同期ファイルのパス

    同期ファイルのパスを設定します。
    ファイル自体の読み込みはwrite_val(), read_val()を初めてした際に読み込まれます。
    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.is_init = True

    def _file_open(self):
        with open(self.file_name, "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0)

    def _make_file(self, dic):
        with open(self.file_name, "w") as f:
            f.write(repr(dic))

    def write_val(self, dic):
        """
        dic: 書き込む辞書

        変数を書き込みます。
        初回実行時に、__init__で指定した同期ファイルが読み込まれます。
        指定したファイルが存在しない場合は新規作成します。

        引数の辞書は、同期ファイル生成時に用いた辞書と同じ形、同じ長さである必要があります。
        """

        if self.is_init:
            self.is_init = False
            try:
                self._file_open()
                print("write_init: file found\n")
            except FileNotFoundError:
                print("write_init: file not found -> make file\n")
                self._make_file(dic)
                self._file_open()

        print("write data -> ", repr(dic).encode())
        self.mm.seek(0)
        self.mm.write(repr(dic).encode())

        # 何らかのエラーで書き込みできなかったときは、再帰的に繰り返す
        if dic == self.read_val():
            return
        else:
            sleep(0.01)
            self.write_val(dic)

    def read_val(self):
        """
        変数を読み込み、辞書型で返します。
        初回実行時に、__init__で指定した同期ファイルが読み込まれます。
        指定したファイルが存在しない場合はNoneを返します。
        """

        if self.is_init:
            self.is_init = False
            try:
                self._file_open()
                print("read_init: file found\n")
            except FileNotFoundError:
                print("read_init: File not found. -> return None")
                return None

        self.mm.seek(0)
        data_byte = self.mm.readline()

        return eval(data_byte.decode('utf-8'))

if __name__ == "__main__":
    global_val = mmap_global_val(file_name="test_file.txt")

    dic = {"testA":0, "testB":[5, 1, 2]}
    global_val.write_val(dic)

    dic_A = global_val.read_val()
    print("data = ", dic_A)

    dic_B = {"testA":5, "testB":[4, 1, 2]}
    global_val.write_val(dic_B)

    dic_C = global_val.read_val()
    print("data = ", dic_C)
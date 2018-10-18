# -*- coding: utf-8 -*-
"""
@author  : smh2208
@time    : 2018/9/20 0:11
"""

import tkinter as tk
from tkinter import ttk, messagebox
from stuhome_spider import StuhomeSpider
import threading, configparser
from time import sleep
from settings import LOG_SUCC, LOG_FAILED

winW = 370
winH = 100


class StuhomeRefresher:
    """
    挂机工具
    """
    def __init__(self):
        self.win = tk.Tk()
        self.win.title('清水河畔挂机工具v0.1.6')
        self.win.protocol('WM_DELETE_WINDOW', self.close_window)
        screensize = self.get_screensize()
        size = '%dx%d+%d+%d' % (winW, winH, (screensize[0] - winW) / 2, (screensize[1] - winH) / 2)
        self.win.geometry(size)
        self.create_widgets()
        self.config = configparser.ConfigParser()
        self.read_userinfo()


    def read_userinfo(self):
        """配置文件读入登录信息"""
        self.config.read('user.ini')
        self.username_in_file = self.config['baseconf']['username']
        self.password_in_file = self.config['baseconf']['password']
        self.username_input.insert(0, self.username_in_file)
        self.password_input.insert(0, self.password_in_file)

    def close_window(self):
        self.win.destroy()

    def get_screensize(self):
        return self.win.winfo_screenwidth(), self.win.winfo_screenheight()

    def create_widgets(self):
        """创建各个gui组件"""
        # frame
        mainframe = tk.Frame(self.win)
        mainframe.grid(padx=10, pady=10)
        topframe = tk.Frame(mainframe)
        topframe.grid(column=0, row=0)
        bottomframe = tk.Frame(mainframe)
        bottomframe.grid(column=0, row=1, columnspan=2)
        # widgets
        username_label = ttk.Label(topframe, text='用户名')
        username_label.grid(column=0,row=0)
        self.username_input = ttk.Entry(topframe, width=20,)
        self.username_input.grid(column=1, row=0)
        password_label = ttk.Label(topframe, text='密码')
        password_label.grid(column=0, row=1, pady=8)
        self.password_input = ttk.Entry(topframe, width=20)
        self.password_input.grid(column=1, row=1)
        self.login_btn_text = tk.StringVar(topframe)
        self.login_btn_text.set('刷新')
        self.login_btn = ttk.Button(topframe, width=8, textvariable=self.login_btn_text, command=self.btn_click)
        self.login_btn.grid(column=2, row=0,rowspan=2, padx=8, ipady=15, sticky='n')
        self.progress_bar = ttk.Progressbar(bottomframe, length=320, maximum=60)
        self.progress_bar.grid(column=0, row=0)

    def btn_click(self):
        """登录按钮点击事件，将用户名和密码写入文件，登录，刷新"""
        if self.login_btn_text.get() == '刷新':
            self.stuhome_sp = StuhomeSpider()
            self.stuhome_sp.stop_sig = False
            self.login_btn_text.set('停止')
            # self.login_btn.state(["pressed"])
            self.login_btn['state'] = 'pressed'
            self.pernament()
            status = self.login()
            if status == LOG_SUCC:
                self.refresh()
            elif status == LOG_FAILED:
                messagebox.showerror('失败', '账号密码错误!')
            else:
                messagebox.showerror('失败', '密码错误次数过多，请 15 分钟后重新登录')
        else:
            self.stuhome_sp.stop_sig = True
            self.login_btn_text.set('刷新')
            self.login_btn['state'] = 'normal'

    def pernament(self):
        """用户名和密码写入本地文件"""
        self.config['baseconf'] = {'username': self.username_input.get(),
                                   'password': self.password_input.get()}
        with open('user.ini', 'w') as f:
            self.config.write(f)

    def show_progress(self):
        """显示进度条"""
        while True:
            if self.login_btn_text.get() == '刷新':
                break
            self.progress_bar.step(1)
            sleep(1)

    def login(self):
        """登录"""
        status = self.stuhome_sp.log_in(self.username_input.get(), self.password_input.get())
        return status

    def refresh(self):
        """刷新首页"""
        refresh_thread = threading.Thread(target=self.stuhome_sp.refresh, daemon=True)
        clock_thread = threading.Thread(target=self.show_progress, daemon=True)
        refresh_thread.start()
        clock_thread.start()


if __name__ == '__main__':
    sr = StuhomeRefresher()
    sr.win.mainloop()
from json import loads
from os import getcwd, makedirs, system
from os.path import isfile, join
from time import time
from tkinter import Label, Tk
from easygui import enterbox
from urllib.request import urlopen, Request
from traceback import print_exc
from matplotlib import pyplot


def 算分(播放, 评论, 弹幕, 收藏, 硬币, 点赞):
    修正B = min(收藏 / 播放 * 250, 50)
    修正C = min(硬币 / 播放 * 150, 20)

    # 播放得点
    基础得分 = 播放
    if 基础得分 > 10000:
        播放得点 = 基础得分 * 0.5 + 5000
    else:
        播放得点 = 基础得分
    if 修正B < 10:
        播放得点 = 播放得点 * 修正B * 0.1

    修正A = ((播放得点 + 收藏) / (播放得点 + 收藏 + 弹幕 * 10 + 评论 * 20)) ** 2

    # 点赞得点
    基础得分 = 点赞
    if 基础得分 > 2000:
        点赞得点 = 基础得分 * 2 + 4000
    else:
        点赞得点 = 基础得分 * 4
    if 修正C < 5:
        点赞得点 = 点赞得点 * 修正C * 0.2

    评论得点 = 评论 * 25 * 修正A
    弹幕得点 = 弹幕 * 修正A
    收藏得点 = 收藏 * 修正B
    硬币得点 = 硬币 * 修正C
    总得点 = 播放得点 + 评论得点 + 弹幕得点 + 收藏得点 + 硬币得点 + 点赞得点
    return locals()


name = {'view': '播放', 'danmaku': '弹幕', 'like': '点赞',
        'coin': '投币', 'favorite': '收藏', 'share': '分享', 'reply': '评论', 'points': '得点'}


def urlget(s):
    return loads(urlopen(Request(s, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'})).read().decode())


class Monitor(Tk):
    stat = {}
    last = {}
    time = 0
    folded = False
    lastclicktime = 0
    points = {'总得点': 0}

    def __init__(self, bv, tm=30, x=200, y=200):
        super().__init__()
        self.bv = bv
        self.tm = tm
        self.x = x
        self.y = y
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(background='black')
        self.geometry(f'300x220+{self.x}+{self.y}')
        self.attributes('-alpha', 0.7)

        self.label1 = Label(self, background='black',
                            foreground='white', text='Loading', wraplength=280)
        self.label2 = Label(self, background='black',
                            foreground='white', text='Loading')
        self.label3 = Label(self, background='black',
                            foreground='white', text='Loading')
        self.label4 = Label(self, background='black',
                            foreground='white', text='Loading')

        for label in (self.label1, self.label2, self.label3, self.label4):
            label.bind('<Button-1>', self.on_click)
            label.bind('<Button-2>', self.refresh)
            label.bind('<Control-Button-1>', self.start_url)
            label.bind('<Button-3>', self.fold)
            label.bind('<B1-Motion>', self.on_move)

        self.label1.place(x=0, y=0, width=300, height=60)
        self.label2.place(x=0, y=60, width=150, height=160)
        self.label3.place(x=150, y=60, width=150, height=160)

        self.after(10, self.main)
        self.mainloop()

    def fold(self, event):
        if self.folded:
            self.folded = False
            self.label4.place(x=0, y=220, width=300, height=60)
            self.geometry(f'300x220+{self.x}+{self.y}')
        else:
            self.folded = True
            self.label4.place(x=0, y=0, width=300, height=60)
            self.geometry(f'300x60+{self.x}+{self.y}')

    def on_move(self, event):
        self.x += event.x-self.lastclickpos.x
        self.y += event.y-self.lastclickpos.y
        self.geometry(f'300x{60 if self.folded else 220}+{self.x}+{self.y}')

    def on_click(self, event):
        if time()-self.lastclicktime < 0.3:
            l = ['播放', '评论', '弹幕', '收藏', '硬币', '点赞']
            pyplot.rcParams['font.sans-serif'] = 'SimHei'
            pyplot.figure(figsize=(4, 3))
            pyplot.pie([self.points[i+'得点']
                       for i in l], labels=[f"{i}：{round(self.points[i+'得点'])}"
                       for i in l])
            pyplot.text(-2, -1, f'修正A：{round(self.points['修正A'], 2)}')
            pyplot.text(-2, -1.2, f'修正B：{round(self.points['修正B'], 2)}')
            pyplot.text(-2, -1.4, f'修正C：{round(self.points['修正C'], 2)}')
            pyplot.show()
        self.lastclickpos = event
        self.lastclicktime = time()

    def start_url(self, event):
        system('start https://www.bilibili.com/video/'+self.bv)

    def refresh(self, event=None):
        try:
            self.time = time()
            data = urlget(
                f'https://api.bilibili.com/x/web-interface/view?bvid={self.bv}')['data']
            if event is not None:
                self.last = self.stat
            self.stat = data['stat']
            if not self.last:
                self.last = self.stat
            self.points = 算分(
                *(self.stat[i]for i in ('view', 'reply', 'danmaku', 'favorite', 'coin', 'like')))
            self.stat['points'] = round(self.points['总得点'])
            csv_file = join(getcwd(), 'bvm_logs', self.bv+'.csv')
            if not isfile(csv_file):
                makedirs('bvm_logs', exist_ok=True)
                with open(csv_file, 'w') as f:
                    print('time', 'exceltime', *name.keys(), sep=',', file=f)
            excel_time = (self.time+8*3600)/86400+70*365+19
            with open(csv_file, 'a') as f:
                print(round(self.time), excel_time, *[self.stat[i]
                                                      for i in name], sep=',', file=f)
            self.title = data['title']
            self.ren = urlget(f"https://api.bilibili.com/x/player/online/total?bvid={
                              self.bv}&cid={data['cid']}")['data']['total']
        except Exception:
            print_exc()

    def main(self):
        if time()-self.time > self.tm:
            self.refresh()
        self.label1.config(text=self.title)
        s = []
        for i in name:
            t = f'{name[i]}:{self.stat[i]}'
            if self.stat[i] != self.last[i]:
                t += f'(+{self.stat[i]-self.last[i]})'
            s.append(t)
        self.label2.config(text='\n'.join(s))
        self.points = 算分(
            *(self.stat[i]for i in ('view', 'reply', 'danmaku', 'favorite', 'coin', 'like')))
        self.label3.config(
            text=f'''{self.bv}
实时观看人数：{self.ren}
Ctrl+单击打开视频
双击查看得点构成
右击折叠窗口
Alt+F4关闭工具
中击立即刷新
距下次刷新{round(self.tm-(time()-self.time), 1)}s''')
        self.label4.config(text=self.title+'\n'+s[0]+' '+s[-1])
        self.after(50, self.main)


if __name__ == '__main__':
    url = enterbox('请输入BV号或视频链接', 'B站视频监视&周刊算分工具')
    bv = [i for i in url.split('/') if i.startswith('BV')][0]
    Monitor(bv)

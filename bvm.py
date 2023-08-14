from json import loads
from os import getcwd, makedirs
from os.path import isfile, join
from sys import argv
from time import time
from tkinter import Label, Tk
from urllib.request import urlopen


class Monitor(Tk):
    def __init__(self, bv, tm=30, x=0, y=0):
        super().__init__()
        self.bv = bv
        self.tm = tm
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(background='black')
        self.geometry(f'150x150+{x}+{y}')
        self.attributes('-alpha', 0.7)
        self.label = Label(self, background='black',
                           foreground='white', text='Loading')
        self.label.place(x=0, y=0, width=150, height=150)
        self.label.bind('<Button-1>', self.on_click)
        self.label.bind('<Button-3>', lambda x: self.destroy())
        self.label.bind('<B1-Motion>', self.on_move)
        self.after(10, self.refresh)
        self.mainloop()

    def on_click(self, event):
        self.lastclick = event

    def on_move(self, event):
        pos_x = self.winfo_x()+event.x-self.lastclick.x
        pos_y = self.winfo_y()+event.y-self.lastclick.y
        self.geometry(f'150x150+{pos_x}+{pos_y}')

    last = {'view': 0, 'danmaku': 0, 'like': 0,
            'coin': 0, 'favorite': 0, 'share': 0, 'reply': 0}
    last_time = 0
    s = ''

    def refresh(self):
        name = {'view': '播放', 'danmaku': '弹幕', 'like': '点赞',
                'coin': '投币', 'favorite': '收藏', 'share': '分享', 'reply': '评论'}
        now_time = time()
        if now_time-self.last_time > self.tm:
            self.last_time = now_time
            data = loads(urlopen(
                f'https://api.bilibili.com/x/web-interface/view?bvid={self.bv}').read().decode())['data']
            stat = data['stat']
            csv_file = join(getcwd(), 'bvm_logs', self.bv+'.csv')
            if not isfile(csv_file):
                makedirs('bvm_logs', exist_ok=True)
                with open(csv_file, 'w') as f:
                    print('时间', *name.values(), sep=',', file=f)
            with open(csv_file, 'a') as f:
                print(round(now_time), *[stat[i]
                      for i in name], sep=',', file=f)
            self.s = (data['title'] if len(data['title']) <=
                      10 else data['title'][:10]+'...')+'\n'
            for i in name:
                self.s += f'{name[i]}:{stat[i]}'
                if stat[i] != self.last[i]:
                    self.s += f'(+{stat[i]-self.last[i]})'
                    self.last[i] = stat[i]
                self.s += '\n'
        self.label.config(
            text=self.s+f'距下次刷新{round(self.tm-(now_time-self.last_time),1)}s')
        self.after(10, self.refresh)


if __name__ == '__main__':
    bv = [i for i in argv[1].split('/') if i.startswith('BV')][0]
    try:
        tm, x, y = map(int, argv[-3:])
        Monitor(bv, tm, x, y)
    except:
        try:
            tm, x = map(int, argv[-2:])
            Monitor(bv, tm, x)
        except:
            try:
                tm = int(argv[-1])
                Monitor(bv, tm)
            except:
                Monitor(bv)

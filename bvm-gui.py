from os import makedirs, system

from easygui import integerbox, textbox

if __name__ == '__main__':
    try:
        with open('bvm_logs/last.txt') as f:
            text = f.read()
    except:
        text = ''
    text = textbox('请输入要监视的 BV 号或链接（每行一个）', 'bvmonitor', text, True)
    if text and (tm := integerbox('请输入刷新间隔', 'bvmonitor', '30', 1, 3600)):
        makedirs('bvm_logs', exist_ok=True)
        with open('bvm_logs/last.txt', 'w') as f:
            f.write(text)
        for i, j in enumerate(text.strip().splitlines()):
            system(f'start bvm.exe {j} {tm} {150*i}')

# coding: utf8

import PySimpleGUI as sg
import time
import vk

# https://oauth.vk.com/authorize?client_id=6478436&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.9
access_token = sg.popup_get_text('Введите ваш токен', font=('Helvetica', 16))
v = '5.95'
session = vk.Session(access_token=access_token)
api = vk.API(session, v=v)

filepath = sg.popup_get_file('Файл с пользователями', font=('Helvetica', 16))
users = open(filepath, 'r', encoding='utf-8', errors='ignore')

group_links = {}
group_saved = {}
deleted = {}
added = {}

for user in users:
    sname = user.split('.com/')[1]
    if (sname[:2] == 'id'): 
        sname = list(sname)
        del sname[:2]
        sname = ''.join(sname)
        
    user_id = api.users.get(user_ids=sname)[0]['id']

    try:
        saved = open(str(user_id) + '.txt', 'r', encoding='utf-8', errors='ignore')
    except FileNotFoundError:
        saved = open(str(user_id) + '.txt', 'w', encoding='utf-8', errors='ignore')
        saved.close()
        saved = open(str(user_id) + '.txt', 'r', encoding='utf-8', errors='ignore')

    try:
        try:
            group_saved[user_id] = eval(saved.read())
            saved.close()
        except SyntaxError:
            pass

        saved = open(str(user_id) + '.txt', 'w', encoding='utf-8', errors='ignore')
        group_links[user_id] = []
        cicles = api.groups.get(user_id=user_id, extended=1, count=200)['count'] // 200
        if (cicles == 0): cicles = 1
        offset = 200

        for i in range(cicles):
            group_links[user_id].extend([g['name'] + ': vk.com/' + g['screen_name'] for g in api.groups.get(user_id=user_id, extended=1, offset=offset*i, count=200)['items']])
            saved.write(str(group_links[user_id]))
            print(len(group_links[user_id]))

            # offset += 200
    except (vk.exceptions.VkAPIError) as e:
        group_links[user_id] = ['Профиль/подписки скрыты']
        saved.write(str(group_links[user_id]), encoding='utf-8')
    
    try:
        diff = list(set(group_links[user_id]) ^ set(group_saved[user_id]))
        deleted[user_id] = []
        added[user_id] = []

        for group in diff:
            if group in group_links[user_id]: added[user_id].append(group)
            if group in group_saved[user_id]: deleted[user_id].append(group)
    except KeyError:
        pass

    saved.close()
    time.sleep(1)
users.close()

layout_main = []
col = [[sg.Multiline(size=(55, 10), key='deleted', font=('Helvetica', 16))], [sg.Multiline(size=(55, 10), key='added', font=('Helvetica', 16))]]

for user_id in group_links:
    layout_main.append([sg.Button(user_id, font=('Helvetica', 16))])

layout_main.append([sg.Multiline(size=(55, 20), key='output', font=('Helvetica', 16)), sg.Column(col)])
layout_main.append([sg.Exit(font=('Helvetica', 16))])

window = sg.Window('Парсер ВК', layout_main)

while True:
    event, values = window.read()
    
    if event in (None, 'Exit'):
        break

    if (int(event) in group_links):
        window['output'].update('Все подписки\n\n'+'\n'.join(group_links[int(event)]))
        try:
            window['deleted'].update('Удаленные\n\n'+'\n'.join(deleted[int(event)]))
            window['added'].update('Добавленные\n\n'+'\n'.join(added[int(event)]))
        except KeyError:
            pass

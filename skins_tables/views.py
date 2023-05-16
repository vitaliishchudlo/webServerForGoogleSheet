import asyncio
import threading

from django.shortcuts import render
from django.urls import reverse
from .models import Skin
import requests
import json

REFRESHING_PROCESS = False

def index(request):
    button_url = reverse('admin:index')
    return render(request, 'index.html', {'button_url': button_url})


def statistics(request):
    skins = Skin.objects.all()
    context = {
        'skins': skins,
    }
    return render(request, 'statistics.html', context)


def refreshing_skins_price():
    skins = Skin.objects.all()
    skin_names = [skin.name for skin in skins]

    skin_prices = {}
    base_link = f'http://18.193.224.198/?skin_name='

    for skin_name in skin_names:
        print('The link: ', base_link + skin_name)
        response = requests.get(base_link + skin_name)
        if response.status_code == 200:
            data = json.loads(response.text)
            skin_price = data.get('skin_price').replace('$', '')
            if not skin_price == 'not found':
                skin_prices[skin_name] = skin_price
                print(skin_name)
                print(skin_price)
        else:
            print('Error:', response.status_code)

    print('Skins prices DICT: ', skin_prices)

    for name, price in skin_prices.items():
        try:
            skin = Skin.objects.get(name=name)
            skin.current_price = price
            skin.save()
        except Skin.DoesNotExist:
            pass


def start_refreshing_skins_price():
    global REFRESHING_PROCESS
    REFRESHING_PROCESS = True

    refreshing_skins_price()

    REFRESHING_PROCESS = False

def refresh(request):

    global REFRESHING_PROCESS
    if REFRESHING_PROCESS:
        return render(request, 'refresh.html', {'refreshing_started': False})
    else:
        thread = threading.Thread(target=start_refreshing_skins_price)
        thread.start()
        return render(request, 'refresh.html', {'refreshing_started': True})



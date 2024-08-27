# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers

import requests

from IDE.models import Slider, NuField, ChField, Block, Robot, Lib


@csrf_exempt
@login_required
def index(request):
    """
    Home page of application IDE.
    Login required.
    Processes requests from frontend and sends requests to NAOqi REST endpoints to communicate with robot Nao.
    """
    response = requests.get("http://localhost:5000/")

    print("\n", response.json())

    # If the request is ajax by checking headers
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If request method is GET, return sliders from database
        if request.method == 'GET':
            sid = request.GET.get('id')
            slider = serializers.serialize('json', Slider.objects.filter(block__name__contains=sid))
            nu_field = serializers.serialize('json', NuField.objects.filter(block__name__contains=sid))
            cha_field = serializers.serialize('json', ChField.objects.filter(block__name__contains=sid))
            data = {
                'slider': slider,
                'nu_field': nu_field,
                'cha_field': cha_field
            }
            return JsonResponse(data, status=200)

        # If request method is POST
        elif request.method == 'POST':
            # If request has key 'stop', stop robot from doing actions
            if request.POST.get('stop'):
                # some functionality...
                pass
            # If request has key 'name', save a sequence to the db
            elif request.POST.get('name'):
                code = save_data(request.POST.get('DTA'))
                b = Block(name=request.POST.get('name'), code=code, alternative="",
                          lib=Lib.objects.get(name="Sekvence"))
                b.save()
            # Else send requests to NAOqi REST API to init connection to robot and execute code
            else:
                data = request.POST.get('DTA')
                rbt = request.POST.get('rbt')
                ip, port, name = robot_init(rbt)
                ### Go to NAOqi Flask endpoint and start connection
                payload = {
                    "ip": ip,
                    "port": port,
                    "name": name
                }
                response = requests.post('http://localhost:5000/init-robot', json=payload)

                print(response.json(), '\n')

                prepare_data(data)

                # Set stop value to False
                # R.stop = False

            return HttpResponse('')

    # Create JSON objects from database models and render home template with them
    lib = serializers.serialize('json', Lib.objects.all())
    all_block = serializers.serialize('json', Block.objects.all())
    robots = serializers.serialize('json', Robot.objects.all())
    data = {
        'all_block': all_block,
        'lib': lib,
        'robots': robots
    }
    return render(request, "../templates/home.html", data)


def robot_init(data: str) -> (str, str, str):
    """
    Gets IP, port and robot name from input data
    """
    split_strings = data.split(" ")
    name = split_strings[0]
    split_strings = split_strings[1]
    split_strings = split_strings.split(":")
    ip = split_strings[0]
    port = split_strings[1]
    return ip, port, name


def save_data(data: str) -> str:
    """
    Processes input data and builds a result code from all blocks.
    """
    split_strings = data.split(";")
    split_strings.pop()
    whole_code = ""
    block_number = 0
    for i in split_strings:  # projde všechny bloky
        splited_i = i.split(":")
        block = Block.objects.filter(name__contains=splited_i[0])[0]
        code_array = splited_i[1].split("^")
        code_array.pop()
        j = 1
        code = block.code
        for cd in code_array:
            code = code.replace("$r" + str(j), cd.split("_")[1])
            code = code.replace("@r", "robot")
            j = j + 1
        block_number += 1
        if (block_number != 1):
            whole_code = whole_code + "\n"
        whole_code = whole_code + code
    return whole_code


def prepare_data(data: str) -> None:
    """
    Prepares data for sending request to NAOqi REST endpoint to execute code.
    """
    split_strings = data.split(";")
    split_strings.pop()
    for i in split_strings:  # projde všechny bloky
        # if not (R.stop):
        splited_i = i.split(":")
        block = Block.objects.filter(name__contains=splited_i[0])[0]
        code_array = splited_i[1].split("^")
        code_array.pop()
        j = 1
        code = block.code
        # Replacing special strings from code with name of robot instance - "robot"
        for cd in code_array:
            code = code.replace("$r" + str(j), cd.split("_")[1])
            code = code.replace("@r", "robot")
            j = j + 1

        # Try to send POST request to NAOqi endpoint
        print(code, '\n')

        payload = {
            "code": code
        }
        response = requests.post('http://localhost:5000/execute', json=payload)
        print(response.json(), '\n')

        if response.json().get("status") == 200:
            print("Code executed successfully on Flask server")
            print("Response:", response.json())
        else:
            print("Failed to execute code on Flask server")
            print("Error response:", response.text)

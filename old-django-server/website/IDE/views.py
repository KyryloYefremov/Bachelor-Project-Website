# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from models import Lib,Block, Sequence, Slider,ChField,NuField,Robot
from django.contrib.auth.decorators import login_required
import time
from django.http import JsonResponse
from json import dumps 
from django.core import serializers
import Robot as R
import math
import requests


@csrf_exempt
@login_required
def index(request):
    response = requests.get("http://localhost:5000/")
    print response.json(), '\n'

    if request.is_ajax(): #Pokud je pozadavek ajax, vrati posuvniky z databaze
        if request.method == 'GET':
            id = request.GET.get('id')
            slider = serializers.serialize('json',Slider.objects.filter(block__name__contains=id))
            nu_field =  serializers.serialize('json',NuField.objects.filter(block__name__contains=id))
            cha_field = serializers.serialize('json',ChField.objects.filter(block__name__contains=id))
            data = {
                'slider' : slider,
                'nu_field':nu_field,
                'cha_field':cha_field
            }
            return JsonResponse(data,status=200)
        elif request.method == 'POST':
            if (request.POST.get('stop')):
                R.stop = True
            elif(request.POST.get('name')):
                Code = save_data(request.POST.get('DTA'))
                b = Block(name=request.POST.get('name'),code=Code,alternative="",lib=Lib.objects.get(name="Sekvence"))
                b.save()
            else:
                ### USING NAOQI API
                data = request.POST.get('DTA')
                rbt = request.POST.get('rbt')
                ip,port,name = robot_init(rbt)
                ### Go to naoqi flask endpoint and start connection
                # robot_class = R.Robot(ip,port,name)
                payload = {
                    "ip": ip,
                    "port": port,
                    "name": name
                }
                response = requests.post('http://localhost:5000/init-robot', json=payload)
                print response.json(), '\n'

                prepare_data(data)
                R.stop = False
            return HttpResponse('')

    lib = serializers.serialize('json',Lib.objects.all())
    all_block = serializers.serialize('json',Block.objects.all())
    robots = serializers.serialize('json',Robot.objects.all())
    data = {
        'all_block' : all_block,
        'lib' : lib,
        'robots' : robots
    }
    return render(request, "../templates/../templates/home.html", data)

def robot_init(data):
        split_strings = data.split(" ")
        name = split_strings[0]
        split_strings = split_strings[1]
        split_strings = split_strings.split(":")
        ip = split_strings[0]
        port = split_strings[1]
        return ip,port,name

def save_data(data):
    split_strings = data.split(";")
    split_strings.pop()
    whole_code = ""
    block_number = 0
    for i in split_strings: #projde všechny bloky
        splited_i = i.split(":")
        block = Block.objects.filter(name__contains=splited_i[0])[0]
        code_array = splited_i[1].split("^")
        code_array.pop()
        j = 1
        code = block.code
        for cd in code_array:
            code = code.replace("$r" + str(j),cd.split("_")[1])
            code = code.replace ("@r","robot")
            j = j + 1
        block_number += 1
        if (block_number != 1) :
            whole_code = whole_code + "\n"
        whole_code = whole_code + code
    return whole_code



def prepare_data(data):
    split_strings = data.split(";")
    split_strings.pop()
    for i in split_strings: #projde všechny bloky
        if (not(R.stop)):
            splited_i = i.split(":")
            block = Block.objects.filter(name__contains=splited_i[0])[0]
            code_array = splited_i[1].split("^")
            code_array.pop()
            j = 1
            code = block.code
            for cd in code_array:
                code = code.replace("$r" + str(j),cd.split("_")[1])
                code = code.replace ("@r","robot")
                j = j + 1
            try:
                ### USING NAOQI API
                # exec(code)
                # Sedning post request to flask server
                print code, '\n'
                payload = {
                    "code": code
                }
                response = requests.post('http://localhost:5000/execute', json=payload)
                print response.json(), '\n'
                if (response.json().get("status") == 200):
                    print("Code executed successfully on Flask server")
                    print("Response:", response.json())
                else:
                    print("Failed to execute code on Flask server")
                    print("Error response:", response.text)

            except Exception, e:
                print "Could not execute code"
                print "Error was: ", e
    
from __future__ import print_function
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy
from django.shortcuts import render, redirect
#from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm

from .models import Acts, Post

#from .models import CustomUser

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import math
import json
import base64
import binascii
from django.core.files import File
import os
from django.core.files.base import ContentFile
import requests
import pickle

import docker


docker_users_ip = 'http://3.210.119.181:80/'

i = 1
ports = []
def create_container():
    global i, ports
    client = docker.from_env()
    #client.images.build(path='', tag='latest')
    container = client.containers.run('acts',
                                      #command='python3 sla_website/manage.py runserver 0.0.0.0:8000',
                                      command = 'ls',
                                      ports = {'8000/tcp':'800'+str(i)},
                                      stderr=True,
                                      stdout=True,
                                      auto_remove=False,
                                      remove=False,
                                      detach=True
                                      )
    log = container.logs(stdout=True, stderr=True, stream=True)
    ports.append('800' + str(i))
    for line in log:
        print(line, end='')
    i += 1
    #container.stop()
    print(container.status)
    #container.remove()

index = -1
def target_server():
    global index, ports
    #if len
    index = (index + 1) % len(ports)
    ipaddr = "http://3.213.12.21:" + ports[index]
    return ipaddr

def auto_scale():
    global ports
    num_requests = 0
    for port in ports:
        r = requests.get(url = ipaddr+port+'/api/v1/acts/_count')
        num_requests += r.content[0]
        requests.delete(url = ipaddr+port+'/api/v1/acts/_count')
    if num_requests<20:
        pass
    else:
        t = math.ceil(num_requests/20)
        while(t):
            create_container()
            t-=1

def timer():
    start = time.time()
    while(1):
        curr = time.time()
        if( (curr - start) >= 120):
            auto_scale()
            start = time.time()




# api/v1/_count
count_req = 0
class CountRequests(APIView):
    def get(self, request):
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/_count')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)
        
    def delete(self, request):
        ipaddr = target_server()
        r = requests.delete(url = ipaddr + '/api/v1/_count')
        return Response(status=r.status_code)


class CountTotalActs(APIView):
    #/api/v1/acts/count
    def get(self, request):
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/acts/count')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)


class IndexView(TemplateView):
    template_name = 'socialmedia/index.html'




#   REST API 
#3. List categories - api/v1/categories
#4. Add categories - api/v1/categories
class ListAddActsCategories(APIView):
    
    def get(self, request, actType=''):
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/categories')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)

    def post(self, request, actType=''):
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/categories', json = data)
        return Response(status=r.status_code)
        

#5. Remove category - /api/v1/categories/{categoryName}
class DeleteActsCategories(APIView):
    def delete(self, request, actType):
        ipaddr = target_server()
        categoryName = self.kwargs.get('actType', None)
        r = requests.delete(url = ipaddr + '/api/v1/categories/' + categoryName, json = request.data)
        return Response(status=r.status_code)
                    

        


#6. List acts for a given category - /api/v1/categories/{categoryName}/acts
#8. List acts in a given range - /api/v1/categories/{categoryName}/acts?start={startRange}&
#end={endRange}

class ListPostAct(APIView):
    def get(self, request, actType, start=0, end=0):
        if request.GET.get('start', None) and request.GET.get('end', None):
            ipaddr = target_server()
            categoryName = self.kwargs.get('actType', None)
            start = request.GET.get('start', None)
            end = request.GET.get('end', None)
            r = requests.get(url = ipaddr + '/api/v1/categories/'+categoryName+'/acts?start='+start+'&end='+end)
            if r.content:
                return Response(data = r.json(), status=r.status_code)
            return Response(status = r.status_code)

        else:
            ipaddr = target_server()
            categoryName = self.kwargs.get('actType', None)
            r = requests.get(url = ipaddr+'/api/v1/categories/' + categoryName + '/acts')
            if r.content:
                return Response(data = r.json(), status=r.status_code)
            return Response(status = r.status_code)


#7. List number of acts for a given category - /api/v1/categories/{categoryName}/acts/size
class ListPostsSize(APIView):
    def get(self, request, actType):
        ipaddr = target_server()
        categoryName = self.kwargs.get('actType', None)
        r = requests.get(url = ipaddr+'/api/v1/categories/' + categoryName + '/acts/size')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)

        
#9. Upvote an act - Route: /api/v1/acts/upvote
class UpvotePost(APIView):
    def post(self, request):
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/acts/upvote', json = data)
        return Response(status=r.status_code)



#10. Remove an act - /api/v1/acts/{actId}
class RemovePost(APIView):

    #/api/v1/acts/{actId}
    def delete(self, request, actID):
        ipaddr = target_server()
        actID = self.kwargs.get('actID', None)
        r = requests.delete(url = ipaddr + '/api/v1/acts/' + actID, json = request.data)
        return Response(status=r.status_code)
        

#11. Upload an act - /api/v1/acts
class AddPost(APIView): 
    def post(self, request):
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/acts', data = data)
        return Response(status=r.status_code)



#api/v1/_health
class HealthCheck(APIView):
    def get(self, request):
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/_health')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)

#api/v1/_crash
class CrashContainer(APIView):
    def post(self, request):
        ipaddr = target_server()
        r = requests.post(url = ipaddr + '/api/v1/_crash')
        return Response(status=r.status_code)

def main():
    ipaddr = "http://3.213.12.21:"
    create_container()
    #print("\n\n\n\n", ports)
    while(1):
        r = requests.get(url = ipaddr+'8001'+'/api/v1/acts/_count')
        if r.content[0]>0:
            break
    x = threading.Thread(target=timer) 
    x.start()

main()
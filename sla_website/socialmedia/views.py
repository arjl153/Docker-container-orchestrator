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
import threading
import docker
import time


docker_users_ip = 'http://3.210.119.181:80/'
num_requests = 0
flag = False

i = 0
ports = []

def create_container(port_number):
    global i, ports
    client = docker.from_env()
    client.images.build(path='/home/ubuntu/docker-acts/', tag='latest')
    print("\n\n\nthis is ports3", ports)
    container = client.containers.run('latest',
                                      command='python3 sla_website/manage.py runserver 0.0.0.0:8000',
                                      #command = 'cat requirements.txt',
                                      ports = {'8000/tcp':port_number},
                                      volumes = {'/home/ubuntu/docker-acts': {'bind': '/code', 'mode': 'rw'}},
                                      name = 'acts-'+str(port_number),
                                      environment = ["TEAM_ID=CC_030_049_056_057"],
                                      stderr=True,
                                      stdout=True,
                                      auto_remove=False,
                                      remove=False,
                                      detach=True
                                      )
    #time.sleep(10)
    print("\n\n\nthis is ports4", ports)
    #log = container.logs(stdout=True, stderr=True, stream=True)
    if container.status == 'created':
        ports.append(str(port_number))
    '''for line in log:
        print(line, end='')'''
    i += 1
    #container.stop()
    print(container.status)

    #container.remove()


index = -1
def target_server():
    global index, ports
    #if len
    index = (index + 1) % len(ports)
    #ipaddr = "http://3.213.12.21:" + ports[index]
    ipaddr = "http://localhost:" + ports[index]
    print("\n\n\nthis is ipaddr", ipaddr)
    return ipaddr

def auto_scale():
    client = docker.from_env()
    ipaddr = "http://3.213.12.21:"
    global ports, num_requests
    print("this is ports", ports)
    
    t = num_requests//20
    t2 = t - (len(ports)-1)
    if(t2>=0):
        print("\n\n\n\nthis is t:", t)
        while(t2):
            create_container(8000+i)
            t2-=1
        #num_requests = 0
    else:
        #t2 - how many containers should i remove? in -ve
        t2 = abs(t2)
        while(t2):
            print("inside remove container")
            name = ports.pop()
            temp_container = client.containers.get('acts-'+name)
            temp_container.stop()
            temp_container.remove()
            t2 -= 1


def timer():
    global num_requests
    timer_flag = 0
    while(1):
        if num_requests==0 and timer_flag == 0:
            continue
        timer_flag = 1
        time.sleep(120)
        auto_scale()
        num_requests = 0

        '''
        start = time.time()        
        curr = time.time()
        if( (curr - start) >= 120):
            auto_scale()
            start = time.time()
        '''


def check_faulty_server():
    client = docker.from_env()
    global ports
    
    ipaddr = "http://3.213.12.21:"
    #print("\n\n\ninside faulty")
    for port in ports:
        print(ipaddr+port + '/api/v1/_health')

        try:
            r = requests.get(url = ipaddr+port + '/api/v1/_health')
        except Exception:
            print("ConnectionRefusedError caught")
            continue


        if r.status_code == 500:
            print("\n\n\ninside status code 500")
            temp_container = client.containers.get('acts-'+port)
            temp_container.stop()
            #client.containers.prune(filter = {})
            temp_container.remove()
            ports.remove(port)
            create_container(int(port))



def timer1():

    start = time.time()
    while(1):
        curr = time.time()
        if( (curr - start) >= 1):
            check_faulty_server()
            start = time.time()


# api/v1/_count
count_req = 0
class CountRequests(APIView):
    def get(self, request):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()

        print("\n\nit came here")
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/_count')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)
        
    def delete(self, request):
        global num_requests
        num_requests += 1

        if flag is False:
            main()

        ipaddr = target_server()
        r = requests.delete(url = ipaddr + '/api/v1/_count')
        return Response(status=r.status_code)


class CountTotalActs(APIView):
    #/api/v1/acts/count
    def get(self, request):
        global num_requests
        num_requests += 1

        if flag is False:
            main()
            
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
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        try:
            r = requests.get(url = ipaddr+'/api/v1/categories', timeout=3)
            if r.content:
                return Response(data = r.json(), status=r.status_code)
            return Response(status = r.status_code)
        except Exception:
            print("api/v1/cat exceptions caught")    
        

    def post(self, request, actType=''):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/categories', json = data)
        return Response(status=r.status_code)
        

#5. Remove category - /api/v1/categories/{categoryName}
class DeleteActsCategories(APIView):
    def delete(self, request, actType):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        categoryName = self.kwargs.get('actType', None)
        r = requests.delete(url = ipaddr + '/api/v1/categories/' + categoryName, json = request.data)
        return Response(status=r.status_code)
                    

        


#6. List acts for a given category - /api/v1/categories/{categoryName}/acts
#8. List acts in a given range - /api/v1/categories/{categoryName}/acts?start={startRange}&
#end={endRange}

class ListPostAct(APIView):
    def get(self, request, actType, start=0, end=0):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
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
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        categoryName = self.kwargs.get('actType', None)
        r = requests.get(url = ipaddr+'/api/v1/categories/' + categoryName + '/acts/size')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)

        
#9. Upvote an act - Route: /api/v1/acts/upvote
class UpvotePost(APIView):
    def post(self, request):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/acts/upvote', json = data)
        return Response(status=r.status_code)



#10. Remove an act - /api/v1/acts/{actId}
class RemovePost(APIView):

    #/api/v1/acts/{actId}
    def delete(self, request, actID):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        actID = self.kwargs.get('actID', None)
        r = requests.delete(url = ipaddr + '/api/v1/acts/' + actID, json = request.data)
        return Response(status=r.status_code)
        

#11. Upload an act - /api/v1/acts
class AddPost(APIView): 
    def post(self, request):
        global num_requests
        num_requests += 1
        
        if flag is False:
            main()
            
        ipaddr = target_server()
        data = request.data
        r = requests.post(url = ipaddr + '/api/v1/acts', data = data)
        return Response(status=r.status_code)



#api/v1/_health
class HealthCheck(APIView):
    def get(self, request):
        if flag is False:
            main()
            
        ipaddr = target_server()
        r = requests.get(url = ipaddr+'/api/v1/_health')
        if r.content:
            return Response(data = r.json(), status=r.status_code)
        return Response(status = r.status_code)

#api/v1/_crash
class CrashContainer(APIView):
    def post(self, request):       
        if flag is False:
            main()
            
        ipaddr = target_server()
        r = requests.post(url = ipaddr + '/api/v1/_crash')
        return Response(status=r.status_code)


def kill_all_containers():
    client = docker.from_env()
    container_list = client.containers.list()
    for c in container_list:
        c.stop()
    client.containers.prune()

def main():
    kill_all_containers()

    global flag
    flag = True
    ipaddr = "http://3.213.12.21:"
    print("\n\n\nthis is ports1", ports)
    create_container(8000)
    print("\n\n\nthis is ports2", ports)
    '''while(1):
        #print("inside wgile")
        #time.sleep(5)
        
        r = requests.get(url = ipaddr+'80'+'/api/v1/_count')
        print("lolololol")
        if r.content[0]>0:
            print("inside if")
            break
        
        if(num_requests>0):
            print("num_requests>0")
            break'''
    x = threading.Thread(target=timer) # for auto scaling
    x.start()

    y = threading.Thread(target=timer1) #for fault tolerance 
    y.start()

main()
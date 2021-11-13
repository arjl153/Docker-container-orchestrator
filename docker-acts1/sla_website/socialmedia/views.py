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

import json
import base64
import binascii
from django.core.files import File
import os
from django.core.files.base import ContentFile
import requests

docker_users_ip = 'http://3.210.119.181:80/'

def list_users():
	ipaddr = docker_users_ip + 'api/v1/users'
	r = requests.get(url =ipaddr)
	data = []
	if r.status_code == 200:
		print(r.text)	
		data = r.json()
	if r.status_code == 204:
		data = []
	return data

count_req = 0

class CountRequests(APIView):
	def get(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		return Response([count_req], status=status.HTTP_200_OK)
	def delete(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req = 0
		return Response(status=status.HTTP_200_OK)

class CountTotalActs(APIView):
	#/api/v1/acts/count
	def get(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		# Needs to be completed
		total_acts = Acts.objects.all().count()
		return Response([total_acts], status=status.HTTP_200_OK)


class IndexView(TemplateView):
	template_name = 'socialmedia/index.html'



#	REST API 
#
#
#



#3. List categories - api/v1/categories
#4. Add categories - api/v1/categories
class ListAddActsCategories(APIView):
	def get(self, request, actType=''):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		acts = Acts.objects.all()

		if(acts.count() == 0):
			return Response(status=status.HTTP_204_NO_CONTENT)

		count = dict()

		for act in acts:
			count[act.actType] = act.post_set.all().count()

		return Response(count, status=status.HTTP_200_OK)

	def post(self, request, actType=''):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		data = request.data
		data = data[0]


		try:
			Acts.objects.get(actType = str(data))
			
		except Acts.DoesNotExist:
			new_act = Acts()
			new_act.actType = str(data)
			new_act.save()

			return Response(status=status.HTTP_201_CREATED)

		return Response(status=status.HTTP_400_BAD_REQUEST)
		

#5. Remove category - /api/v1/categories/{categoryName}
class DeleteActsCategories(APIView):
	def delete(self, request, actType):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		data = self.kwargs.get('actType', None)

		try:
			act = Acts.objects.get(actType = str(data))

		except Acts.DoesNotExist:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		act.delete()
		return Response(status=status.HTTP_200_OK)
					

		


#6. List acts for a given category - /api/v1/categories/{categoryName}/acts
#8. List acts in a given range

class ListPostAct(APIView):
	def get(self, request, actType, start=0, end=0):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		if request.GET.get('start', None) and request.GET.get('end', None):
			print("in this shit\n\n\n")
			data = self.kwargs.get('actType', None)
			#startRange = self.kwargs.get('start', None)
			#endRange = self.kwargs.get('end', None)

			startRange = int(request.GET.get('start', None))
			endRange = int(request.GET.get('end', None))
			print('This is startrange', startRange)
			print('This is endrange', endRange)
			try:
				acts = Acts.objects.get(actType = str(data))
			except Acts.DoesNotExist:
				return Response(status = status.HTTP_204_NO_CONTENT)


			no_of_posts = acts.post_set.count()
			print('\n\n\n\n', no_of_posts)
			if(startRange < 1 or endRange > no_of_posts):
				return Response(status = status.HTTP_400_BAD_REQUEST)

			count = endRange-startRange+1
			if count > 100:
				return Response(status = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
			if count < 1:
				return Response(status = status.HTTP_400_BAD_REQUEST)
			
			count2 = 0
			response_data = []
			for post in reversed(acts.post_set.all()):
				if(count2 == count or count2 == no_of_posts):
					break;

				response_dict = dict()
				response_dict = {
					'username': str(post.user),
					'timestamp': post.timestamp,
					'actId': post.id,
					'caption': post.caption,
					#'imgB64': base64.b64encode((post.image).file.read())
					'imgB64': post.image
				}
				response_data.append(response_dict)
				count2 += 1

			return Response(response_data, status = status.HTTP_200_OK)

		else:
			#----------------------
			data = self.kwargs.get('actType', None)
			
			act = Acts.objects.get(actType = data)
			count = act.post_set.all().count()

			
			if(count >= 500):
				return Response(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
			elif(count == 0):
				return Response(status=status.HTTP_204_NO_CONTENT)	
			
			response_dict= dict()
			response_data = []

			for post in act.post_set.all():
				#print("usernmae", post.user)
				response_dict = {
					'username': str(post.user),
					'timestamp': post.timestamp,
					'actId': post.id,
					'caption': post.caption,
					#'imgB64': base64.b64encode((post.image).file.read())
					'imgB64': post.image
				}
				'''response_dict['actId'] = post.id
				response_dict['caption'] = post.caption
				response_dict['imgB64'] = base64.b64encode((post.image).file.read())'''
				response_data.append(response_dict)

			return Response(response_data, status=status.HTTP_200_OK)


#7. List number of acts for a given category - /api/v1/categories/{categoryName}/acts/size
class ListPostsSize(APIView):
	def get(self, request, actType):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		data = self.kwargs.get('actType', None)
		
		acts = Acts.objects.all()

		try:
			act = Acts.objects.get(actType = str(data))

		except Acts.DoesNotExist:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		count = act.post_set.all().count()
		return Response(count, status=status.HTTP_200_OK)


		

'''
#8. Return number of acts for a given category in a given range (inclusive) - /api/v1/categories/{categoryName}/acts?start={startRange}&end={endRange}

class ListPostRange(APIView):
	def get(self, request, actType, startRange, endRange):
		data = self.kwargs.get('actType', None)
		startRange = self.kwargs.get('startRange', None)
		endRange = self.kwargs.get('endRange', None)
		print('This is endrange', endRange)
		try:
			acts = Acts.objects.get(actType = str(data))
		except Acts.DoesNotExist:
			return Response(status = status.HTTP_204_NO_CONTENT)


		no_of_posts = Acts.objects.all().count()
		#print('\n\n\n\n', no_of_posts, EndRange)
		if(startRange < 1 or endRange > no_of_posts):
			return Response(status = status.HTTP_400_BAD_REQUEST)

		count = endRange-startRange+1
		if(count > 100 or count < 1):
			return Response(status = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
		
		count2 = 0
		response_data = []
		for post in acts.post_set.all.reversed():
			if(count2 == count or count2 == no_of_posts):
				break;

			response_dict = dict()
			response_dict = {
				'username': str(post.user),
				'timestamp': post.timestamp,
				'actID': post.id,
				'caption': post.caption,
				#'imgB64': base64.b64encode((post.image).file.read())
				'imgB64': post.image
			}
			response_data.append(response_dict)
			count2 += 1

		return Response(response_data, status = status.HTTP_200_OK)
'''

#9. Upvote an act - Route: /api/v1/acts/upvote

class UpvotePost(APIView):
	def post(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		postID = request.data[0]
		print('\n\n\n\n lol')
		try:
			post = Post.objects.get(id = postID)

		
		except Post.DoesNotExist:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		post.upvotes += 1
		post.save()
		return Response(status = status.HTTP_200_OK)



#10. Remove an act - /api/v1/acts/{actId}

class RemovePost(APIView):

	#/api/v1/acts/{actId}
	def delete(self, request, actID):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		#actID is post.id here!!!

		data = self.kwargs.get('actID', None)
		#data = request.data
		try:
			post_del = Post.objects.get(pk = data)
			post_del.delete()
			return Response(status=status.HTTP_200_OK)

		except Post.DoesNotExist:
			return Response(status=status.HTTP_400_BAD_REQUEST)


#11. Upload an act - /api/v1/acts
class AddPost(APIView):	
	def post(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		global count_req
		count_req += 1
		# Getting list of users from docker users
		users = list_users()
		
		data = request.data
		

		actID = data.get('actId')
		
		username = str(data.get('username'))
		actType = str(data.get('categoryName'))
		timestamp = data.get('timestamp')
		caption = data.get('caption')
		imgB64 = data.get('imgB64')
		
		

		posts = Post.objects.all()

		if actID in posts.values_list('id', flat=True):
			print("\n\n\n1")
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		if username not in users:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
			
		try:
			image_binary = base64.b64decode(imgB64)
		except binascii.Error:
			print("\n\n\n 2")
			return Response(status=status.HTTP_400_BAD_REQUEST)


		new_post = Post()

		new_post.act = Acts.objects.get(actType = str(actType))
		new_post.user = username
		new_post.id = actID
		new_post.caption = caption
		new_post.image = imgB64
		
		#timestamp read is in the format of “DD-MM-YYYY:SS-MM-HH”,
		dd = timestamp[0:2]
		mm = timestamp[3:5]
		yy = timestamp[6:10]
		ss = timestamp[11:13]
		minm = timestamp[14:16]
		hh = timestamp[17:19]

		#2019-02-09 11:17:13
		new_timestamp = yy+"-"+mm+"-"+dd+" "+hh+":"+minm+":"+ss
		print("\n\n\n\n\n", new_timestamp)

		try:
			new_post.timestamp = new_timestamp
			new_post.save()

		except:
			print("\n\n\n 3")
			return Response(status=status.HTTP_400_BAD_REQUEST)	

		return Response(status=status.HTTP_201_CREATED)


# Project APIS
def is_container_crash():

	try:
		f = open('container_status', 'r')
	except FileNotFoundError:
		return 0
		
	content = f.read()
	f.close()
	if(content == "1"):
		return 1
	else:
		return 0

class HealthCheck(APIView):
	def get(self, request):
		if(is_container_crash()):
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		else:
			return Response(status=status.HTTP_200_OK)

class CrashContainer(APIView):
	def post(self, request):
		f = open('container_status', 'w')
		f.write("1")
		f.close()
		return Response(status=status.HTTP_200_OK)
		
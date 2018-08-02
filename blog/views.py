from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.utils import json
from django.contrib.auth.models import User as U
from django.contrib.auth.hashers import make_password

from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated


class ProfileList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    name = 'profile-list'
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileDetailSerializer
    name = 'user-detail'
    http_method_names = ['get']


class ProfilePostList(generics.ListCreateAPIView):
    name = 'profile-post-list'
    queryset = User.objects.all()
    serializer_class = ProfilePostSerializer
    http_method_names = ['post', 'get']

    def get(self, request, user_pk, format=None):
        snippet = Post.objects.filter(owner_id=user_pk).all()
        serializer = PostSerializer(snippet, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, user_pk, format=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Token does not exist'}, status=401)

        data = JSONParser().parse(request)
        serializer = SinglePostSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


class ProfilePostDetail(generics.RetrieveUpdateAPIView):
    name = 'post-detail'
    queryset = Post.objects.all()
    serializer_class = UpdatePostSerializer
    http_method_names = ['get', 'put', 'delete']

    def get(self, request, user_pk, pk, format=None):
        try:
            post = Post.objects.get(id=pk, owner_id=user_pk)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)

    def put(self, request, user_pk, pk, format=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Token does not exist'}, status=401)

        try:
            post = Post.objects.get(id=pk, owner_id=user_pk)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)

        current_user_id = self.request.user.id
        if not post.is_owner(current_user_id):
            return Response({'error': 'Unauthorized'}, status=401)

        serializer = UpdatePostSerializer(post, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

    def delete(self, request, user_pk, pk, format=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Token does not exist'}, status=401)

        try:
            post = Post.objects.get(id=pk, owner_id=user_pk)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        current_user_id = self.request.user.id
        if not post.is_owner(current_user_id):
            return Response(status.HTTP_401_UNAUTHORIZED)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfilePostAllList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfilePostsSerializer
    name = 'profile-post-all'
    http_method_names = ['get']


class ProfilePostCommentList(generics.ListAPIView):
    name = 'comment-list'
    queryset = Comment.objects.all()
    serializer_class = ProfilePostCommentListSerializer
    http_method_names = ['get']

    def get(self, request, user_pk, post_pk, format=None):
        snippet = Comment.objects.all().filter(post_id=post_pk).prefetch_related('post', 'post__owner')
        serializer = ProfilePostCommentListSerializer(snippet, many=True, context={'request': request})
        return Response(serializer.data)


class ProfilePostCommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = ProfilePostCommentDetailSerializer
    name = 'comment-detail'

    def get(self, request, user_pk, post_pk, pk, format=None):
        snippet = Comment.objects.get(id=pk, post_id=post_pk, post__owner_id=user_pk)
        serializer = ProfilePostCommentDetailSerializer(snippet, many=False, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, user_pk, post_pk, pk, format=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Token does not exist'}, status=401)

        try:
            comment = Comment.objects.get(id=pk, post_id=post_pk, post__owner_id=user_pk)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        current_user_id = self.request.user.id
        if not comment.post.is_owner(current_user_id):
            return Response(status.HTTP_401_UNAUTHORIZED)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InfoPostList(generics.ListAPIView):
    name = 'info-post-list'
    queryset = User.objects.all()
    serializer_class = InfoPostListSerializer
    http_method_names = ['get']


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return Response({
            'profiles': reverse(ProfileList.name, request=request),
            'posts': reverse(ProfilePostAllList.name, request=request),
            'info-posts': reverse(InfoPostList.name, request=request),
         })


def ImportaDB(request):
    # json_data = json.load(open('db.json').read())

    dump_data = open('db.json', 'r')
    as_json = json.load(dump_data)

    for user in as_json['users']:
        geo = Geo.objects.create(lat=user['address']['geo']['lat'],
                                 lng=user['address']['geo']['lng'])
        address = Address.objects.create(street=user['address']['street'],
                                         suite=user['address']['suite'],
                                         city=user['address']['city'],
                                         zipcode=user['address']['zipcode'],
                                         geo=geo)
        user_obj = U.objects.create(username=user['username'], password=make_password("Aa123456"), email=user['email'], last_login="2018-08-01 00:00")
        print(user['email'])
        User.objects.create(
            name=user['name'],
            address=address,
            owner=user_obj)

    for post in as_json['posts']:
        user = User.objects.get(id=post['userId'])
        Post.objects.create(id=post['id'],
                            title=post['title'],
                            body=post['body'],
                            owner=user)

    for comment in as_json['comments']:
        post = Post.objects.get(id=comment['postId'])
        Comment.objects.create(id=comment['id'],
                               name=comment['name'],
                               email=comment['email'],
                               body=comment['body'],
                               post=post)

    dump_data = open('db.json', 'r')
    as_json = json.load(dump_data)
    for user in as_json['users']:
        geo = Geo.objects.create(lat=user['address']['geo']['lat'],
                                 lng=user['address']['geo']['lng'])
        address = Address.objects.create(street=user['address']['street'],
                                         suite=user['address']['suite'],
                                         city=user['address']['city'],
                                         zipcode=user['address']['zipcode'],
                                         geo=geo)

        user = User(id=user['id'],
                    name=user['name'],
                    email=user['email'],

                    address=address)
        user.save()

    for post in as_json['posts']:
        usuario = User.objects.get(id=post['userId'])

        Post.objects.create(id=post['id'],
                            title=post['title'],
                            body=post['body'],
                            owner=usuario)

    for comment in as_json['comments']:
        post = Post.objects.get(id=comment['postId'])
        Comment.objects.create(id=comment['id'],
                               name=comment['name'],
                               email=comment['email'],
                               body=comment['body'],
                               post=post)

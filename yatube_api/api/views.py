from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, filters, generics
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsOwnerOrReadOnly
from posts.models import Group, Post, Follow, User
from .serializers import \
    CommentSerializer, GroupSerializer, \
    PostSerializer, FollowSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_post(self):
        return get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

    def get_queryset(self):
        return self.get_post().comments


class FollowViewSet(viewsets.ViewSetMixin, ListCreateAPIView):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('^following__username',)
    ordering_fields = ('following',)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Follow.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from general.models import User, Post
from rest_framework import serializers

class UserRegisterationSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      "username",
      "password",
      "email",
      "first_name",
      "last_name",
    )
  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
    )
    user.set_password(validated_data['password'])
    user.save()

    return user

class UserListSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      "id",
      "first_name",
      "last_name",
      "username"
    )

class NestedPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "created_at",
        )

class UserRetrieveSerializer(serializers.ModelSerializer):
  is_friend = serializers.SerializerMethodField()
  friend_count  = serializers.SerializerMethodField()
  posts = NestedPostListSerializer(many=True)

  class Meta:
    model = User
    fields = (
      "id",
      "first_name",
      "last_name",
      "email",
      "is_friend",
      "friend_count",
      "posts"
    )

  def get_is_friend(self, obj)->bool:
     return obj in self.context['request'].user.friends.all()

  def get_friend_count(self, obj)->int:
    return obj.friends.count()
  


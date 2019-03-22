from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serailizer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Created user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user



class AuthTokenSerializer(serializers.ModelSerializer):
    """Serializer for user authentication object"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')

    email = serializers.CharField()
    password = serializers.CharField(
        style= {'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            message = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(message, code='authentication')

        attrs['user'] = user
        return attrs
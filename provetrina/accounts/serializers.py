from django.contrib.auth import password_validation
from rest_framework import serializers

from provetrina.accounts.models import User


def _get_falsy_field_value_err_msg(falsy):
    if falsy == '':
        return 'This field may not be blank.'
    return 'This field is required.'


class UserSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'password_confirmation',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
            }
        }

    def validate_password(self, password):
        """Validate the password via Django's default validators."""
        password_validation.validate_password(
            password,
            self.instance,
            password_validation.get_default_password_validators(),
        )
        return password

    def validate(self, attrs: dict):
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')
        if password and not password_confirmation:
            err_msg = _get_falsy_field_value_err_msg(password_confirmation)
            err = {'password_confirmation': err_msg}
            raise serializers.ValidationError(err)
        if password_confirmation and not password:
            err_msg = _get_falsy_field_value_err_msg(password)
            err = {'password': err_msg}
            raise serializers.ValidationError(err)
        if password != password_confirmation:
            err_msg = 'Password confirmation does not match the password'
            err = {'password_confirmation': err_msg}
            raise serializers.ValidationError(err)
        return super().validate(attrs)

    def create(self, validated_data: dict):
        validated_data.pop('password_confirmation', '')
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data: dict):
        user = instance
        validated_data.pop('password_confirmation', '')
        password = validated_data.pop('password', '')
        if password:
            user.set_password(password)
            user.save()
        return super().update(user, validated_data)

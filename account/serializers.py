from rest_framework import serializers
from account.models import User
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=User
        fields=['email','name','password','password2','tc']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        if password!=password2:
            raise serializers.ValidationError('Passwords doesnot matched')
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=User
        fields=['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','name']

class UserChangePasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    
    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        user=self.context.get('user')
        if password!=password2:
            raise serializers.ValidationError('Passwords doesnot matched')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    
    class Meta:
        fields=['email',]

    def validate(self, attrs):
        email=attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User not exists with the given email")
        user=User.objects.get(email=email)
        uid=urlsafe_base64_encode(force_bytes(user.id))
        print("Encode UID is ",uid)
        token=PasswordResetTokenGenerator().make_token(user)
        print("Token ",token)
        link='http://localhost:3000/api/user/reset/'+uid+'/'+token
        print(link)
        send_mail('Password Change Request', 'Your Password Reset Link is: {}'.format(link), settings.EMAIL_HOST_USER, [email])
        return attrs

class UserPasswordResetSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    
    def validate(self, attrs):
        try:
            password=attrs.get('password')
            password2=attrs.get('password2')
            uid=self.context.get('uid')
            token=self.context.get('token')
            if password!=password2:
                raise serializers.ValidationError('Passwords doesnot matched')
            
            id=smart_str(urlsafe_base64_decode(uid))
            user=User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Invalid Token or Token Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as Identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Invalid Token or Token Expired")

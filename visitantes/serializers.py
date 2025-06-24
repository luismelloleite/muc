from rest_framework import serializers
from .models import Visitante

class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = '__all__'

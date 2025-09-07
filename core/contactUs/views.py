# django files

# rest files
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action as Action
from rest_framework.response import Response
# your files
from .models import  ContactInfo, SocialLink, Honors, License
from .serializers import (
    ContactInfoSerializer,
    SocialLinkSerializer, HonorsSerializer, LicenseSerializer,
)



class ContactViewSet(viewsets.ModelViewSet):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    @Action(detail=True, methods=['get'])
    def get_social_links(self, request, pk=None):
        contact = self.get_object()
        social_links = SocialLink.objects.filter(contact=contact)
        serializer = SocialLinkSerializer(social_links, many=True)
        return Response(serializer.data)


class SocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer




class HonorViewSet(viewsets.ModelViewSet):
    queryset = Honors.objects.all()
    serializer_class = HonorsSerializer

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer



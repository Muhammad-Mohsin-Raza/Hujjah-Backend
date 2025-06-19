from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Defendant
from .serializers import DefendantSerializer


class DefendantListCreateView(generics.ListCreateAPIView):
    queryset = Defendant.objects.all()
    serializer_class = DefendantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DefendantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Defendant.objects.all()
    serializer_class = DefendantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            # Partial=True makes all fields optional
            return self.update(request, *args, **kwargs, partial=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            return self.destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

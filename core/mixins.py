from rest_framework.response import Response


class StandardResponseMixin:
    """
    Wraps list/retrieve/create/update/destroy responses from ModelViewSet
    into a consistent { success, message, data } format.
    """

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Fetched successfully',
            'data': response.data
        }, status=response.status_code)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Fetched successfully',
            'data': response.data
        }, status=response.status_code)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Created successfully',
            'data': response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Updated successfully',
            'data': response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Deleted successfully',
            'data': None
        }, status=200)
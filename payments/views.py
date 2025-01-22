import hashlib
from rest_framework import status
import uuid
from accounts.models import  Register, Referral, ReferralReward
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PaymentSerializer
from video.serializers import ParticipantSerializer
import requests
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from payments.models import PaymentDetails
from video.models import Participant
from wallet.models import ReferrelPaymentHistory




class PaymentCreateGetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        competition = request.data.get('competition')
        tci = request.data.get('tci')
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            register = Register.objects.filter(user=request.user).first()
            # if competition:
            if tci:
                participant = Participant.objects.filter(user=register, competition__id=tci).first()
            else:
                participant = Participant.objects.filter(user=register, competition__id=competition).first()
            # else:
                # participant = Participant.objects.filter(user=register, tournament__id=tournament).first()
            # if not participant:
            #     return Response({'message': 'You are not registered for this competition'}, status=status.HTTP_400_BAD_REQUEST)

            participant.is_paid = True
            if participant.temp_video:
                participant.video = participant.temp_video
                participant.temp_video = None
            participant.save()
            payment = PaymentDetails.objects.filter(txnid=request.data.get('txnid'), user=register).first()
            payment.participant = participant
            payment.save()

            # apply referrel
            referrel = Referral.objects.filter(invitee=register, status='pending').first()
            referrel_amount = ReferralReward.objects.last()
            if referrel and referrel_amount:
                ReferrelPaymentHistory.objects.create(amount=referrel_amount.amount, referrel=referrel)
                referrel.inviter.points += referrel_amount.amount
                referrel.invitee.points += referrel_amount.amount
                referrel.inviter.save()
                referrel.invitee.save()
                referrel.status = 'confirmed'
                referrel.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = Register.objects.filter(user=request.user).first()
        payments = PaymentDetails.objects.filter(user=user)
        payments_serializer = PaymentSerializer(payments, many=True)
        return Response(payments_serializer.data, status=status.HTTP_200_OK)
    

    
@csrf_exempt
def successview(request):
    return render(request, 'success.html')


@csrf_exempt
def failure(request):
    return render(request, 'failure.html')






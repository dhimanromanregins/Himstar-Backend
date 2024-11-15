import hashlib
from rest_framework import status
import uuid
from accounts.models import  Register
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PaymentSerializer
import requests
from bs4 import BeautifulSoup


class MakePaymentView(APIView):
    def get(self, request):
        # Extract competition_id and user_id from query params
        competition_id = request.query_params.get('competition_id', None)
        user_id = request.query_params.get('user_id', None)
        price_param = request.query_params.get('price', None)

        if not competition_id:
            return Response({"error": "competition_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            # Fetch user details
            user = Register.objects.get(id=user_id)
        except Register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        unique_id = uuid.uuid4()

        # Convert UUID to a string
        unique_id_str = str(unique_id)
        print(unique_id_str)

        print(unique_id_str)
        api_key = "t108UM"
        salt = "dWwGvm4Bv5bEsQpZWVtheoJIZyYgZ68W"
        txn_id = unique_id_str
        amount = price_param
        product_info = competition_id
        first_name = user.first_name
        email = user.email
        phone = user.mobile_number
        surl = "http://localhost:3000/success"
        furl = "https://test-payment-middleware.payu.in/simulatorResponse"

        # Create the hash string
        hash_string = f"{api_key}|{txn_id}|{amount}|{product_info}|{first_name}|{email}|||||||||||{salt}"
        hash = hashlib.sha512(hash_string.encode()).hexdigest()
        # print(f"Generated Hash: {hash}")

        # Payment gateway URL
        url = "https://test.payu.in/_payment"

        # Prepare the payload for the request
        payload = {
            "key": api_key,
            "txnid": txn_id,
            "amount": price_param,
            "productinfo": product_info,
            "firstname": first_name,
            "email": email,
            "phone": phone,
            "surl": surl,
            "furl": furl,
            "hash": hash
        }


        # Send the request to the payment gateway with redirects disabled
        response = requests.post(url, data=payload, allow_redirects=False)

        # Capture the 'Location' header from the response
        redirect_url = response.headers.get('Location')
        # print(f'Redirect URL: {redirect_url}')

        # Check if the response status code is 302 (redirect)
        if response.status_code == 302 and redirect_url:
            # Return the redirect URL as part of the response
            return Response({"message": "Payment initiated", "redirect_url": redirect_url}, status=status.HTTP_200_OK)
        else:
            # Return error response if payment initiation failed
            return Response({"error": "Failed to initiate payment", "response": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PaymentCallbackView(APIView):
    def post(self, request):
        # Get the payment_url and coupon from request data
        payment_url = request.data.get("payment_url")
        coupon = request.data.get("coupon")

        print(payment_url, '55555555', coupon)

        if not payment_url:
            return Response({"error": "Payment URL not provided"}, status=status.HTTP_400_BAD_REQUEST)

        response = requests.get(payment_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        form_tag = soup.find('form')

        if form_tag:
            # Extract necessary data from the form
            txn_id = form_tag.find('input', {'name': 'txnid'})['value']
            amount = form_tag.find('input', {'name': 'amount'})['value']
            mode = form_tag.find('input', {'name': 'mode'})['value']
            product_info = form_tag.find('input', {'name': 'productinfo'})['value']
            firstname = form_tag.find('input', {'name': 'firstname'})['value']
            email = form_tag.find('input', {'name': 'email'})['value']
            phone = form_tag.find('input', {'name': 'phone'})['value']
            payment_status = form_tag.find('input', {'name': 'status'})['value']
            mihpayid = form_tag.find('input', {'name': 'mihpayid'})['value']
            card_category = form_tag.find('input', {'name': 'cardCategory'})['value']

            # Process payment data
            payment_data = {
                'txn_id': txn_id,
                'mihpayid': mihpayid,
                'amount': amount,
                'mode': mode,
                'product_info': product_info,
                'firstname': firstname,
                'email': email,
                'phone': phone,
                'status': payment_status,
                'card_category': card_category,
                'coupon': coupon
            }

            # Serialize and save payment details
            serializer = PaymentSerializer(data=payment_data)

            if serializer.is_valid():
                serializer.save()
                # Check if the payment was successful before sending an email
                if payment_status.lower() == "success":
                    # Prepare the email content (you can create a template for the invoice)
                    subject = "Your Payment Invoice"
                    message = render_to_string('payment_invoice_email.html', {
                        'txn_id': txn_id,
                        'amount': amount,
                        'mode': mode,
                        'product_info': product_info,
                        'firstname': firstname,
                        'email': email,
                        'phone': phone,
                        'mihpayid': mihpayid,
                        'card_category': card_category,
                        'coupon': coupon
                    })

                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,  # Sender email
                        [email],  # Receiver email
                        fail_silently=False,
                    )

                    return Response({"message": "Payment details saved and invoice sent successfully"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "Payment failed, no invoice sent"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("No form tag found on this page.")
            return Response("No form tag found on this page.", status=status.HTTP_400_BAD_REQUEST)






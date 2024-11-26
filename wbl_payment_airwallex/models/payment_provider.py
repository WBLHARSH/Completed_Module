# -*- coding: utf-8 -*-
#
#################################################################################
# Author      : Weblytic Labs Pvt. Ltd. (<https://store.weblyticlabs.com/>)
# Copyright(c): 2023-Present Weblytic Labs Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
##################################################################################

from odoo import fields, models
import requests
from odoo.exceptions import ValidationError


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('airwallex', "Airwallex Payment Gateway")], ondelete={'airwallex': 'set default'}
    )

    airwallex_client_id = fields.Char(
        string="Client Id",
        required_if_provider='airwallex')

    airwallex_api_key = fields.Char(
        string="Api Key",
        required_if_provider='airwallex')

    def bearerToken(self):
        auth_url = "https://api-demo.airwallex.com/api/v1/authentication/login"
        auth_payload = {}
        auth_headers = {
            "Content-Type": "application/json",
            "x-api-key": self.airwallex_api_key,
            "x-client-id": self.airwallex_client_id
        }
        try:
            auth_response = requests.post(auth_url, headers=auth_headers, json=auth_payload)
            auth_response.raise_for_status()  # Raise an exception for HTTP errors

            if auth_response.status_code == 201:
                token = auth_response.json().get('token')
                return token
            else:
                return None
        except requests.exceptions.HTTPError as http_err:
            raise ValidationError(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            raise ValidationError(f"Error occurred: {req_err}")
        except Exception as err:
            raise ValidationError(f"An error occurred: {err}")

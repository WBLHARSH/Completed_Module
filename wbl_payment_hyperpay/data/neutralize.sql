-- disable hyperpay payment provider
UPDATE payment_provider
   SET hyperpay_merchant_id = NULL,
       hyperpay_merchant_id_mada = NULL,
       hyperpay_authorization_bearer = NULL;

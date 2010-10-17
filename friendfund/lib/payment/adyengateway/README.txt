Adyen Payment Gateway interface for Python
==========================================

    >>> obj = AdyenPaymentGateway(
    ...     url='https://pal-test.adyen.com/pal/servlet/soap/Payment',
    ...     user='ws@Company.YourCompany', password='YourPassword',
    ...     merchantAccount='MerchantAccount',
    ... )

    >>> obj.authorise('T-2', 100, 'EUR', 'FABIO TRANCHITELLA',
    ...     '5555444433331111', '12', '2012', '737', ipAddress='127.0.0.1')
    {'authCode': ... }

    >>> print obj.cancel('8112083591854919')
    True

    >>> print obj.capture('8112083586124880', 100, 'EUR')
    True

    >>> print obj.refund('8112083586124880', 100, 'EUR')
    True


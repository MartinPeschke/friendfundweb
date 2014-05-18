import logging
from datetime import datetime
import socket
import re

import formencode
from pylons import app_globals as g
from pylons import session as websession
from babel.numbers import parse_decimal, NumberFormatError, format_currency, format_decimal

from friendfund.model.mapper import DBMappedObject
from friendfund.model.pool import PoolUser, InsufficientParamsException
from friendfund.lib.payment.adyen import PaymentMethod
from friendfund.lib.tools import sanitize_html, decode_minimal_repr


enlocal = re.compile('^(([0-9]{1,3}\,?([0-9]{3}\,?)+)|[0-9]*)(\.[0-9]{2})?$')
delocal = re.compile('^(([0-9]{1,3}\.?([0-9]{3}\.?)+)|[0-9]*)(\,[0-9]{2})?$')
emailmatcher = re.compile('^([0-9a-zA-Z]+([-._][0-9a-zA-Z]+)*@[0-9a-zA-Z]+([-._][0-9a-zA-Z]+)*[.][a-zA-Z]{2,9})$')
socket.setdefaulttimeout(5)

log = logging.getLogger(__name__)
strbool = formencode.validators.StringBoolean(if_missing=False)
_ = lambda x:x

class TOSValidator(formencode.validators.StringBoolean):
    messages = {"need_to_agree": _('TOSVALIDATOR_You have to agree to our terms and conditions.')}
    def _to_python(self, value, state):
        value = strbool.to_python(value)
        if not value:
            raise formencode.Invalid(self.message("need_to_agree", state), value, state)
        return value

class ReceiverValidator(formencode.FancyValidator):
    messages = {"missing_receiver_data": _('FF_PARTNERIFRAME_ERROR_TITLE_Please select a recipient!')}
    def _to_python(self, value, state):
        try:
            value = PoolUser.from_map(decode_minimal_repr(value))
        except (AttributeError, TypeError, InsufficientParamsException), e:
            raise formencode.Invalid(self.message("missing_receiver_data", state), value, state)
        return value


class PWDValidator(formencode.validators.String):
    messages = {"invalid_chars":_('PWDVALIDATOR_Please dont input any special characters.')}
    def _to_python(self, value, state):
        super(self.__class__, self)._to_python(value, state)
        try:
            str(value)
        except UnicodeEncodeError,e:
            raise formencode.Invalid(self.message("invalid_chars", state), value, state)
        return value

class DateValidator(formencode.FancyValidator):
    messages = {"invalid_date":_('DATEVALIDATOR_Please input Date in Valid Format YYYY-MM-DD')}
    def _to_python(self, value, state):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            raise formencode.Invalid(self.message("invalid_date", state), value, state)
        return value

class CurrencyValidator(formencode.FancyValidator):
    messages = {"invalid_currency":_('CURRENCYVALIDATOR_Please input a valid Currency')}
    def _to_python(self, value, state):
        if not value in g.country_choices.currencies:
            raise formencode.Invalid(self.message("invalid_currency", state), value, state)
        return value

class DecimalValidator(formencode.FancyValidator):
    messages = {"invalid_amount":_('MONETARYVALIDATOR_Please input a valid amount'),
                "amount_too_high":_("Please enter a number that is %(max_amount)s or smaller"),
                "amount_too_low":_("Please enter a number that is %(min_amount)s or higher")
    }
    def _to_python(self, value, state):
        try:
            value = float(parse_decimal(value, locale = websession['lang']))
            if self.max and value > self.max:
                raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=websession['lang'])), value, state)
            if self.min and value < self.min:
                raise formencode.Invalid(self.message("amount_too_low", state, min_amount = format_decimal(self.min, locale=websession['lang'])), value, state)
        except NumberFormatError, e:
            raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
        except ValueError, e:
            raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=websession['lang'])), value, state)
        else: return value

class DecimalStringValidator(DecimalValidator):
    def _to_python(self, value, state):
        value = super(self.__class__, self)._to_python(value, state)
        return format_decimal(value, locale=websession['lang'])

class SanitizedHTMLString(formencode.validators.String):
    messages = {"invalid_format":_('There was some error in your HTML!')}
    def _to_python(self, value, state):
        value = super(self.__class__, self)._to_python(value, state)
        try:
            return sanitize_html(value)
        except Exception, e:
            log.error("HTML_SANITIZING_ERROR %s", value)
            raise formencode.Invalid(self.message("invalid_format", state, value = value), value, state)


class MonetaryValidator(formencode.validators.Number):
    messages = {"invalid_amount":_('MONETARYVALIDATOR_Please input a valid amount'),
                "amount_too_high":_("Please enter a number that is %(max_amount)s or smaller")
    }
    def _to_python(self, value, state):
        try:
            value = float(parse_decimal(value, locale = websession['lang']))
        except NumberFormatError, e:
            raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
        else:
            if value > self.max:
                raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_currency(self.max, state.currency, locale=websession['lang'])), value, state)
            else:
                super(self.__class__, self)._to_python(value, state)
        return value

def to_displaymap(obj):
    if obj is None: return {}
    if not isinstance(obj, DBMappedObject):
        raise Exception('Object not of expected type %s instead of %s' % (obj, DBMappedObject.__name__))
    result = {}
    for k in obj._keys:
        value = getattr(obj, k.pykey, None)
        if value:
            result[k.pykey] = value
    return result

class SettlementValidator(formencode.validators.FormValidator):
    settlementOption = 'settlementOption'
    __unpackargs__ = ('settlementOption',)
    messages = {
    'MissingAField': _("SETTLEMENT_PAYPAL_EMAIL_MISSIN_Please enter a valid value"),
    'InvalidOption': _("SETTLEMENT_Invalid Settlement Option")
    }

    def validate_python(self, field_dict, state):
        errors = self._validateReturn(field_dict, state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            raise formencode.Invalid(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in error_list]),
                field_dict, state, error_dict=errors)

    def _validateReturn(self, field_dict, state):
        settlementOption = field_dict[self.settlementOption]
        values = field_dict.get(settlementOption)
        errors = {}
        try:
            so = state.request.merchant.map[settlementOption]
        except KeyError, e:
            errors["settlementOption"] = self.message('InvalidOption', state)
        else:
            for field in so.required_fields:
                try:
                    field.validator.to_python(values[field.name])
                except KeyError, e:
                    errors["settlementOption"] = self.message('MissingAField', state)
                except formencode.Invalid, e:
                    errors[settlementOption] = errors.get(settlementOption, {})
                    errors[settlementOption][field.name] = e
        return errors


class PaymentMethodValidator(formencode.validators.String):
    messages = {"payment_method_invalid":_("unsupported payment method")}
    def _to_python(self, value, state):
        super(self.__class__, self)._to_python(value, state)
        pm = state.payment_methods.get(value)
        if not (pm and isinstance(pm, PaymentMethod)):
            raise formencode.Invalid(self.message("payment_method_invalid", state), value, state)
        return value


class TotalTransactionCostValidator(formencode.validators.FormValidator):
    contrib_baseAmount = 'baseAmount'
    contrib_totalAmount = 'totalAmount'
    contrib_method = 'method'

    __unpackargs__ = ('contrib_baseAmount', 'contrib_totalAmount','contrib_method')
    messages = {
    'notANumber': _("Please enter a valid amount"),
    'TotalsDontAddUp': _("Invalid Totals"),
    'UnSupportedPaymentMethod': _("unsupported payment method")
    }
    def validate_python(self, field_dict, state):
        errors = self._validateReturn(field_dict, state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            raise formencode.Invalid(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in error_list]),
                field_dict, state, error_dict=errors)

    def _validateReturn(self, field_dict, state):
        baseAmount = field_dict[self.contrib_baseAmount]
        totalAmount = field_dict[self.contrib_totalAmount]
        method = field_dict[self.contrib_method]

        pm = state.payment_methods.get(method)
        if not (pm and isinstance(pm, PaymentMethod)):
            return {self.contrib_method: self.message('UnSupportedPaymentMethod', state)}
        try:
            assert pm.check_totals(baseAmount, totalAmount)
        except ValueError:
            return {self.contrib_totalAmount: self.message('notANumber', state)}
        except AssertionError:
            log.warning('TotalsDontAddUp:%s,%s,%s', baseAmount, totalAmount, pm)
            return {self.contrib_totalAmount: self.message('TotalsDontAddUp', state)}
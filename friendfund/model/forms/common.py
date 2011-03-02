import formencode, md5, logging
from datetime import datetime
import dns.resolver, socket, re
from pylons import app_globals as g
from pylons.i18n import _
from friendfund.model.mapper import DBMappedObject
from friendfund.lib.payment.adyen import PaymentMethod
from pylons import session as websession

from babel.numbers import parse_decimal, NumberFormatError, format_currency

enlocal = re.compile('^(([0-9]{1,3}\,?([0-9]{3}\,?)+)|[0-9]*)(\.[0-9]{2})?$')
delocal = re.compile('^(([0-9]{1,3}\.?([0-9]{3}\.?)+)|[0-9]*)(\,[0-9]{2})?$')
emailmatcher = re.compile('^([0-9a-zA-Z]+([-._][0-9a-zA-Z]+)*@[0-9a-zA-Z]+([-._][0-9a-zA-Z]+)*[.][a-zA-Z]{2,9})$')
socket.setdefaulttimeout(5)

log = logging.getLogger(__name__)
strbool = formencode.validators.StringBoolean(if_missing=False)

class TOSValidator(formencode.validators.StringBoolean):
	def _to_python(self, value, state):
		value = strbool.to_python(value)
		if not value:
			raise formencode.Invalid(_('TOSVALIDATOR_You have to agree to our terms and conditions.'), value, state)
		return value


class PWDValidator(formencode.validators.String):
	def _to_python(self, value, state):
		super(self.__class__, self)._to_python(value, state)
		try:
			str(value)
		except UnicodeEncodeError,e:
			raise formencode.Invalid(_('PWDVALIDATOR_Please dont input any special characters.'), value, state)
		return value

class DateValidator(formencode.FancyValidator):
	def _to_python(self, value, state):
		try:
			value = datetime.strptime(value, '%Y-%m-%d')
		except:
			raise formencode.Invalid(
				_('DATEVALIDATOR_Please input Date in Valid Format YYYY-MM-DD'), value, state)
		return value

class CurrencyValidator(formencode.FancyValidator):
	def _to_python(self, value, state):
		if not value in g.country_choices.currencies:
			raise formencode.Invalid(
				_('CURRENCYVALIDATOR_Please input a valid Currency'), value, state)
		return value

class DecimalValidator(formencode.validators.Number):
	def _to_python(self, value, state):
		try:
			value = parse_decimal(value, locale = websession['lang'])
		except NumberFormatError, e:
			raise formencode.Invalid(
				_('MONETARYVALIDATOR_Please input a valid amount'), value, state)
		else: return value

class MonetaryValidator(formencode.validators.Number):
	def _to_python(self, value, state):
		try:
			value = parse_decimal(value, locale = websession['lang'])
		except NumberFormatError, e:
			raise formencode.Invalid(
				_('MONETARYVALIDATOR_Please input a valid amount'), value, state)
		else:
			if value > self.max:
				raise formencode.Invalid(_("Please enter a number that is %s or smaller") % format_currency(self.max, state.currency, locale=websession['lang']), value, state)
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
	messages = {
		'MissingAField': _("Please enter a valid value"),
		'InvalidOption': _("Invalid Settlement Option")
		}

	def validate_python(self, field_dict, request):
		errors = self._validateReturn(field_dict, request)
		if errors:
			error_list = errors.items()
			error_list.sort()
			raise formencode.Invalid(
				'<br>\n'.join(["%s: %s" % (name, value)
							   for name, value in error_list]),
				field_dict, state, error_dict=errors)

	def _validateReturn(self, field_dict, request):
		settlementOption = field_dict["settlementOption"]
		
		errors = {}
		try:
			so = request.merchant.map[settlementOption]
		except:
			return {"settlementOption": self.message('InvalidOption', request)}
		else:
			for rf in so.required_fields:
				if not rf.is_valid(field_dict['%s.%s' % (so.name, rf.name)]):
					errors['%s.%s' % (so.name, rf.name)] =  self.message('MissingAField', request)
		return errors
	
	
class PaymentMethodValidator(formencode.validators.String):
	def _to_python(self, value, state):
		super(self.__class__, self)._to_python(value, state)
		pm = state.payment_methods.get(value)
		if not (pm and isinstance(pm, PaymentMethod)):
			raise formencode.Invalid(_("unsupported payment method"), value, state)
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

class Message(object):
	def __init__(self, msg):
		self.msg = msg

class ErrorMessage(Message):
	is_error=True
class SuccessMessage(Message):
	is_error=False

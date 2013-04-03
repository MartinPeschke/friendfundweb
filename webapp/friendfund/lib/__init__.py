def map_update_dict(key, value):
	def setter(somedict):
		somedict[key] = value
		return somedict
	return setter
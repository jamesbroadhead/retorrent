def price(watts,day_price, night_price):
	return (watts/1000) * ((day_price*13) + (night_price*9)) * 365

# ASSUME: usage is continuous
# ASSUME: month is 30 days
def kWhr_to_watts(kWhrs,months):
	# 1 unit = 1 kW for 1 hour
	# 100 kW for 1hr == 100 units
	# 1 kW for 100 hrs == 100 units
	Whrs = 1000*float(kWhrs)
	hours = (30*months)*24

	W = Whrs / hours
	
	return W

def main(watts):
	print price(watts,0.1706,0.0844)



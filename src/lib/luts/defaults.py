# Lookup tables for default values that are not null/none/false/0

defaults = {
#Objects
	#96:149, # can be None
	#248:-1,
	350:30,
	#356:138, # can be None? but also can be instantiated and it will be ignored
	561:227,
	659:109,
	1245:477, # can be None, I think
	1248:144, # master track
	1250:269,
	2444:617,
	2445:616,
	2447:615,
	2450:88,
	3033:215,
	#5702:1594, # can be None
	6411:1751,
	6841:1754,
	6842:1754,
	6846:1929,
	#6226:1694,
	#7189:558, # can be None

	# Done automatically when an atom is created
	#612:17, # can be None
	#6194:236, # can be None

# Booleans
	2727:True, # not necessary
	3070:True, # not necessary
	3021:True, # not necessary
	4991:True, # not necessary, but a nice thing to do
	4992:True, # not necessary
	6309:True,
	6310:True,

# Integers
	4803:2,
	4804:-2,
	7499:0x10000024,

# Strings
	"branch":"releases",
}

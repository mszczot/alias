import alias as al

def generate_semi_stables(af):
	potential_completes = []
	allin = af.generate_all_in()
	
	def transition_step(a, L):
		L.outargs.add(a)
		L.inargs.remove(a)
		for arg in L.outargs.copy():
			if L.af.get_arg_obj(arg).is_illegally_out(L):
				L.undecargs.add(arg)
				L.outargs.remove(arg)

	def find_completes(L):

		if L.is_complete():
			return
			
		illegal = False
		for arg in L.inargs:
			if L.af.get_arg_obj(arg).is_illegally_in(L):
				illegal = True
				break
		if not illegal:
			for ldash in potential_semi_stables:
				if L.undeclabels <= ldash.undeclabels:
					potential_semi_stables.remove(ldash)
			potential_semi_stables.append(L)
			return
		else:
			sii = set()
			for arg in L.inargs:
				if L.af.get_arg_obj(arg).is_super_illegally_in(L):
					sii.add(arg)
			if sii:
				transition_step(sii.pop(), L)
				find_semi_stables(L)
			else:
				for arg in L.inargs.copy():
					if arg in L.inargs:
						if L.af.get_arg_obj(arg).is_illegally_in(L):
							transition_step(arg, L)
							find_semi_stables(L)

	find_completes(allin)
	return potential_completes
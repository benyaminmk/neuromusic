# connect muse headset using address
# address found by turning Muse on and running in a terminal `sudo hcitool lescan`
ADDRESS= "00:55:DA:B7:74:0D"

connect:
	@python muse-lsl.py --address ${ADDRESS}


collect:
	@python collect_data.py

# helper fcn to update requirements.txt if new packages are being used in this project
overwrite_reqs:
	@echo -n "are you sure you're in the right env to overwrite requirements.txt? [y/n]" && read ans && [ $${ans:-n}=y ]
reqs: overwrite_reqs
	@$(shell conda list -e > ../requirements.txt)
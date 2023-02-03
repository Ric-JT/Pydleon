# Pydleon
Pydleon is not refactored garbanzo

# Load personal Idleon data into Pydleon
1. Go to Idleon Efficiency and download the raw data as a json in resources/**raw_data.json**.
1. Run <code> python read_raw_json.py </code> to build the resources/**cake.json**.
1. Run <code> python test_features.py </code> to test the functionalities.
    * You can run with the <code> -i </code> so you can interact with the program in python thorugh the terminal.

# Functionalities:
* Read Character Bag
* Read Chest
* Define grindlist
* Get grindleft and grindcost
* Get cost of a set of items
* Get crafting procedire of a set of items with total cost
    

import shelve

stovedata = shelve.open("stove_info.shelve", writeback=True)
if (not "devices" in stovesensor_data):
        stovesensor_data["devices"] = {}

def create_code():
    completed = False
    while (not completed):
        uid = 0
        for i in range(0, 4):
            number = random.randint(1, 9)
            uid = uid * 10 + number
        if (uid not in stovedata["devices"]):
            stovedata["devices"][uid] = {}
            completed = True
    return uid
    
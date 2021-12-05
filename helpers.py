import googlemaps
gmaps = googlemaps.Client(key = "AIzaSyClT-Fnn4-iW9HIJjY-XBVemrJCjLoqgxE")

#All 50 US State abbreviations (used a few times throughout)
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

# Splices datetimes into an integer list of the form [year, month, day, hour, minute]
def time_splicer(now):
    date_components = now[0].split('-')
    time_components = now[1].split(':')

    now = date_components + time_components

    # Get rid of the "seconds" entry of now, if present
    if len(now) > 5:
        del now[-1]

    # Convert to ints
    for number in now:
        number = int(number)

    return now

def find_protests(origin, protests_raw, proximity=0):
    # initialize variables for while loop
    i = 0
    protests = []
    
    # Only append protests within desired proximity
    while i < len(protests_raw):
        destination_lat_lng = str(protests_raw[i]["lat"]) + ", " + str(protests_raw[i]["lng"])
        location = gmaps.reverse_geocode(destination_lat_lng)[i]["formatted_address"]
        
        destination = [(protests_raw[i]["lat"], protests_raw[i]["lng"])]
        
        distance = int(gmaps.distance_matrix(origin, destination, units="imperial")['rows'][0]['elements'][0]['distance']['text'].split()[0])

        if distance <= proximity or proximity==0: 
            protests.append({"issue":protests_raw[i]["issue"], "location":location, "start":protests_raw[i]["start"], "distance":distance})
        
        i += 1
    return protests




# Getting started
From the beginning, I knew that I was planning on building a flask-based web app. As such, to get the ball rolling, I used CS50 finance as a template of sorts. This made a lot of the CSS a lot easier--I just had to modify existing CSS to suit my needs.

I will now go page by page to describe my design choices.

# The login page
The layout of the login page is adapted from Bootstrap's example login page. I didn't want the logo (designed by my good friend Swathi Kella) to only be a favicon, so you'll notice that on this login page (and a few others) it is featured prominently above the relevant page information.

User experience is about more than just aesthetics, though. I wanted to create a journey for each user. I've designed by app such that if you try to access any of its routes without being logged in, you are redirected to the login page. I did this by checking if session["user_id"] returned anything and redirecting accordingly using flask. This essentially prevents "sequence breaking" and ensures every user that is using the website has and is logged into an Apptivism account. Users that don't yet have an account can easily be redirected to the register page by clicking the hyperlink featured prominently above the login form.

The flask route associated with this page has two methods: GET and POST. Accessing via GET will just render the login page. POST logs the user in, records the session (so that they don't have to keep logging back in), and redirects them to the protest organizing page.

Also note that this page has its own associated css file. This is due to the fact that this page was directly adapted from Bootstrap's example. Using styles.css would have interfered with some of its styling.

# The register page
The layout of the register page was again adapted from Bootstrap. I wanted to make sure there was a consistent theme of your eyes being drawn to the center of each webpage. Additionally, I wanted the form itself to fit together snugly without being too vertical. I managed to do this using Bootstrap's grid system in html.

This flask route has two methods associated with it: GET and POST. GET just renders the template for the register page. POST, on the other hand, triggers some data checking systems to make sure that the user has completed all required forms with valid information. Checking if usernames or emails were taken was as simple as checking the database for any emails or usernames that match the ones retrieved with request.form.get(). If there are any, users are notified that that email/username is already taken (by rendering the register template with the previously blank error message variables set equal to a string containing the error message). If there aren't, the program moves onto the next checkpoint: ensuring that the email address actually has an "@" and "." somewhere in there. Similar checks are performed to ensure other parameters were submitted and valid.

Once all checks have been passed, the send_verification() function is called. As the name suggests, it sends a verification email to users. It does this using the flask_mail library (configured via my config.cfg to connect to apptivismbot@gmail.com). The send_verification() function is defined toward the top of the app.py file instead of helpers.py because it relies on the flask app itself to function. I couldn't figure out how to import the app (as in app = Flask(__name__)) to helpers.py to make the flask_mail library functional there, so I ultimately just decided leave it at the top of the app.py file. This function is used a couple times so I abstracted it away for readability's sake.

Also note that instead of typing every state abbreviation for the address dropdown selector, I just googled a list of state abbreviations in python list format, copied it into helpers.py, and had flask render register.html with each state abbreviation using a for loop.

# Verifying email
The link sent to users in the verification email is a unique link. Its specific address varies with respect to token created when running s.dumps(users_email) and, since everyone has a unique email, everyone will have a unique token.

Clicking the link brings users to the "/confirm_email/<token>" route. Here, python tries to load the token. However, if the email was sent over 24 hours ago, SignatureExpired will trigger and the user will be shown a page telling them that their confirmation link has expired and that they can click a hyperlink to have it resent.

If the token has not expired, the user will be redirected to the "/confirmed" route. This route takes methods GET and POST. When arrived to via GET (e.g. by redirection), Apptivism first checks to make sure that the user hasn't already confirmed their email address. If they have (as determined by querying SQL to see if the 'confirmed' column associated with this user's id is 'true'), they will be redirected to the "/organize" route (for organizing protests). If they have not already verified their email address, verification is performed by updating the SQL database and then they are presented with a webpage notifying them that their address has been confirmed.

This webpage has a form where users can indicate which social issues they are passionate about. Upon indicating this, the POST route is triggered and this information will be stored in the passions table of the SQL database.

The reason I wanted the confirmed page to only be accessible by users who are confirming their email addresses for the first time is because otherwise, the passions table in the SQL database could end up with duplicate entries for the same user. This would result in the page on the "/organize" route having duplicate entries for social issues because this page is rendered by querying the database for the user's passions and then using jinja syntax to add each passion to the webpage.

# Organizing a protest
This is the default page that logged in, verified users are sent to when visiting Apptivism. The dropdown menu for what issue the user wants to protest is unique to that user, and is accomplished using the method described in the last paragraph of the previous section. The checking system to make sure that every box is filled out and valid is similar to that which is described for the register system.

What I do want to focus on, though, is the system that checks that the protest's proposed start time hasn't already passed. To do this, I first split the current datetime (acquired using datetime.now()) into a list containing YYYY-MM-DD and hour:min:seconds to separate them (by first converting the datetime into a string and then using the .split() attribute). I then ran the time_splicer() function that I wrote (found in helpers.py) to further split this into list containing [YYYY, MM, DD, hour, min]. Next, I split the submitted datetime using using a similar process. The only differences being that I acquired the submitted datetime using request.form.get("start_datetime") and that my initial split was done along "T" instead of " " since the form formats it as YYYY-MM-DDThour:min. Now that both the present time and the submitted time were converted into lists, I looped through them comparing each value. If the submitted time was less than the current time at any point, the loop breaks and the error message is triggered. If the loop finishes without any issues, the protest information is stored in the protests table of the SQL database and the user is notified that their protest has been successfully organized.

# Finding a protest
When accessing this page via "GET," you will be presented with a dropdown selector requesting you to choose the maximum distance away you want protests to be. For this section, I'd like to focus on how I implemented the function that filters the protests presented to the user after they submit their proximity preference.

I made sure to design the dropdown menu so that any distance preferences started with a number. The "any distance" option is the only one that doesn't. This way, if a user selects a distance preference, the numerical value can be easily acquired by performing .split() and then converting the first entry in the resulting list to an int.

I acquired the user's origin by querying the users table for latitude and longitude in the SQL database. I then formatted this origin as [(lat, lng)] because I knew that I would be using gmaps.distance_matrix() to get the distance between two points. Even though I only cared about two points, the function only takes matrices as inputs——hence the format of origin.

I then queried the SQL database for the issue, latitude, longitude, and start time of every protest in the protests table whose central issue is also found in the user's indicated passions (as found in the passions table). This output was set equal to a variable called protests_raw.

Then, if their indicated proximity preference was "any distance" I called the find_protests function with arguments origin and protests_raw. By not specifying proximity, the function (found in helpers.py) knows to set it equal to 0. This function then goes through every protest in the protests_raw list of dicts, acquires the formatted address of the protest using gmaps.reverse_geocode(), acquires the matrix-formatted location of the protest, and determines the distance (in miles) between the user's origin and the location of the protest using gmaps.distance_matrix().

Then, the list "protests" is appended with a dict containing the protest's issue, location (as a formatted address), start time, and distance.

The same process is followed if the user indicates a specific proximity, the only difference being that the each protest is only appended if the distance is belowing the maximum requested distance.

The output of this find_protests() function is the list of dicts "protests" which is ultimately used to render the template that displays the information of relevant protests.


Welcome to Apptivism!

# What is Apptivism?
Apptivism is a web application that allows users with registered accounts and verified email addresses to organize and discover information about protests near them.
A full overview can be viewed here: https://www.youtube.com/watch?v=VKe5ArKWGJE .

# How do I get started?
To start using Apptivism, you must first ensure that your terminal is in the "Apptivism" directory. I recommend running Apptivism from your computer locally instead of CS50 IDE because the flask-mail library (which controls the email verification system) will start misbehaving otherwise. From there, just run the command "flask run" and click on the link it returns. 

# Registering an account
Since this is your first time visiting the website, you will end up on the "login" page. But you don't yet have an account! Not to worry, just click on the "here" in "No account? Register here!" This text should be located above the login form. Upon clicking the hyperlink, you will be redirected to the register page. This form requires a valid email address, unique username, a password that is at least 8 characters long & contains at least one digit, confirmation of that password, and home address. If a user tries to register with any values left blank or failing to meet Apptivism's requirements, they will be notified with a light red error message indicating what issue they must resolve to proceed with registration.

# Verifying your email address
If you try to access Apptivism's protest organizing and discovery pages without verifying your email address, you will be redirected to the verification failure page. Upon redirection, the verification email will be automatically resent to you, so please check your email for the verification link. Clicking the link will verify your account's email address as long as 24 hours haven't elapsed since the email was originally sent. If your confirmation link has expired, you will find yourself on a page that notifies you as such and gives you the option to have a new link sent to you. Click the "here" in "resend here" and your confirmation link will be resent to you and you will be redirected to a page notifying you as such. 

# Indicating passions
Once you have successfully verified your email address, you will find yourself on a page that asks that you to indicate what social issues you are passionate about. Your selection determines the issues for which you can attend and organize protests—-all issues left unselected will be filtered out. Choose wisely—-this page can only be accessed once!

# Organizing a protest
Upon indicating your passions, you will be immediately taken to the "organize protest" page. Here, you can get the word out for your protest by indicating the protest's central issue, where it is taking place, and when it starts! If anything is left blank, you will receive an error message and be asked to try again. Similarly, if your protest's start time takes place before the present, you will receive an error message informing you that unless you're a time traveler, your protest should take place in the future—not the past!

# Finding a protest
To find a protest, simply navigate to the "Find Protest" tab. First, you will be asked to indicate the maximum distance you would like the protest to be. Don't leave this blank--you will receive an error message! If proximity isn't a concern "any distance" is one of the options in the proximity drop down menu, so there's no reason not to make a choice! Your choice will determine which protests you will be shown. Upon indicating your preferred protest proximity, you will be shown a list of protests that match your previously listed passions and are within your preferred distance. Happy protesting!

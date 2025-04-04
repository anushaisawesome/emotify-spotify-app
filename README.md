# emotify-spotify-app

to run:
<br><br>
first <b>install dependencies</b> in backend.py and d.py 
<br><br>
do this by running this in a new terminal for <b> windows </b>:
<code>
pip install flask pandas numpy tf spotipy keras sklearn requests scipy
</code>
<br>
alternatively do this by running this in a new terminal for <b> macos </b>:
<code>
pip3 install flask pandas numpy tf spotipy keras sklearn requests scipy
</code>
or try:
<code>
python3 -m pip install
</code>
if pip3 doesn't work.
<br><br>
then run backend.py first, and go to the link the Flask server is hosted on. you will need to log into <a href='https://open.spotify.com/'> spotify web player </a>, and open chrome developer tools (F12 on <b>windows </b>, cmd + shift + I on <b>macos</b>.) <br>find a tab that says 'network', and under it will be a burst of requests that happens on your logging in. <br>once this subsides, open a request with name 'events', and scroll until you see 'Authorisation'.<br> <b> copy the chunk of text after 'Bearer', this is your access token. </b>
<br><br>
paste this token into the field on the homepage, <b> open developer tools </b> and click a point on the plane.<br> if you have the python file open alongside your browser, you can see the request being passed and the neural network being trained.<br> once this is done, a string of letters and numbers will appear as a request in developer tools. click on in, and scroll to where it says 'Request URL'. <br> <b>this is the link to your generated playlist</b>. <br> copy-paste into a new tab and enjoy!


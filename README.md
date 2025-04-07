# emotify-spotify-app

<b>to run:</b>
<br><br>
first <b>install python dependencies</b> 
<br><br>
do this by running this in a new terminal for <b> windows </b>:
```
pip install flask pandas numpy tensorflow spotipy keras sklearn requests scipy
```
<br>

alternatively do this by running this in a new terminal for <b> macos </b>:
```
pip3 install flask pandas numpy tf spotipy keras sklearn requests scipy
```
or try:
```
python3 -m pip install
```
if pip3 doesn't work.
<br><br>
then run backend.py first, and go to the link the Flask server is hosted on. you will need to log into  <a href='https://open.spotify.com/'>spotify web player</a> , and open chrome developer tools (F12 on <b>windows </b>, cmd + option + I on <b>macos</b>.) <br>find a tab that says 'network', and under it will be a burst of requests that happens on your logging in. <br>once this subsides, open a request with name 'events', and scroll until you see 'Authorisation'.<br> <b> copy the chunk of text after 'Bearer', this is your access token. </b>
<br><br>
paste this token into the field on the homepage, click submit and <b>click a point on the plane</b> on the next page.<br> if you have the python file open alongside your browser, you can see the request being passed and the neural network being trained.<br>a playlist will then be generated with the 10 emotionally closest songs in your Spotify listening history to the point you chose. <br>once your playlist has been generated, you should be redirected its Spotify page, where you can decide what to do with it.
<br><br><br>
<b>generating more playlists:</b>
<br><br>
once you have generated your first playlist, files will have been created with the tracks in your library, which the neural network has processed. <br>thus, for any further playlists you wish to make, <b>quit the server running on backend.py, and run d.py instead</b>. <br>this ensures that for every new playlist you wish to generate by clicking the canvas, the model isn't being retrained and the files aren't being regenerated from scratch. <br>the initial process of this happening can feel quite time-consuming, so once backend.py has been run once on your data there is no need to rerun it in order to make more playlists.
<br><br><br><br>
<b>happy playlisting! :)</b>





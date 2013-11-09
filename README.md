
# Storage API

This repository holds the storage api for the n64 analytics engine.

It is responsible for maintaining a database of user sessions, user races,
events that take place, as well as tracking where in blob storage videos
have gotten to.

It does not currently work.

## Features

This api offers a number of useful features.

* Object tracking
* Video Splitting
* Event querying

Currently item 1 works for Sessions and Races, and item 2 works to some
degree. Events are not tracked yet, and will be in future versions. Video
splitting currently is kind of dumb. This will also be improved later.

## REST usage

There a couple of REST endpoints available currently

* `/sessions` provides a list of all sessions
* `/sessions/<session_id>` gives a single session
* `/sessions/<session_id>/races` is a list of races
* `/sessions/<session_id>/split_races` splits a session video into races
* `/races/<race_id>` is a single race


The individual item endpoints (`/sessions/<session_id>` and
`/races/<race_id>`) support GET, PUT, and DELETE. 

* GET returns the object as JSON
* PUT accepts JSON in the request body and updates the object, note that
  only some of the objects properties may be updated. 
* DELETE deletes the object

For the list of items, GET and POST are accepted

* GET returns a list of objects in a JSON list
* POST creates a new object of the given type and returns the new objects id

Session objects have the following attributes available, bold items are
required.

* video_url: a url where the video file can be found

Race objects accept the following key/value pairs for creation and update,
bold items are required.

* **start_time**: When in the session the race starts in seconds
* **duration**: race duration in seconds
* video_url: the url of where the video can be found

If you want to split a session into races, you should POST to
`/sessions/<session_id>/split_races`. This will use ffmpeg to split out
each race and will update the races with the new URL of the race with where
it should be able to be accessed.

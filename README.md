
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

Currently item 1 is under way.

## REST usage

There a couple of REST endpoints available currently

* `/sessions` provides a list of all sessions
* `/sessions/<session_id>` gives a single session
* `/sessions/<session_id>/races` is a list of races
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

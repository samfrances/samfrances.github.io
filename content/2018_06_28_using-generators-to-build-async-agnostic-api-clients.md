Title: Using generators to build async agnostic API clients
Date: 2018-6-28 20:02
UniqueId: 2018-6-28-using-generators-to-build-async-agnostic-api-clients-55ebbf4a-2f8a-4a70-be38-00cc1b8e025e
Modified:
Category: Blog
Tags: python, asyncio, async
Slug: using-generators-to-build-async-agnostic-api-clients
Authors:
Summary: A strategy for building API client libraries that work in async and sync contexts

I'm a big fan of asyncio, couroutines and `async`/`await` syntax in
Python 3.5+. However, they come with some well documented downsides. Not least
among these is the
[red/blue function problem](http://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/).
Coroutines can call plain functions, but only a coroutine can await another
coroutine (unless you count running it by directly invoking the event loop).
Meanwhile, if a coroutine calls a plain function which triggers some sort of
blocking IO, the whole event loop is blocked.

I have found the red/blue divide particularly annoying in the context of web
API clients. Take [boto3](https://boto3.readthedocs.io/), the popular client for
AWS's various APIs. This only works in a synchronous context (unless you don't
mind blocking the event loop for the duration of each request). Another project,
[aiobotocore](https://github.com/aio-libs/aiobotocore), provides some of these
capabilities in an async context, but doesn't support all services and operations.

Yet, many of the things API clients do have nothing directly to do with IO,
async or otherwise. Preparing a HTTP request - determining what headers to
use, constructing a request body, calculating signatures and other
authentication details - is a purely functional, IO-free business.
The same goes for interpreting a HTTP response.

A function or method in an API client is like a sandwich where constructing
the request and interpreting the response are the two pieces of bread, and sending
the request is the filling. We ought to be able to use the same bread for any
type of sandwich, without caring if the filling is ham, cheese, or something else.

Ok, enough with the shaky metaphors. Time for some code.

The strategy I have stumbled upon is to write the pure
request-construction / response-interpretation logic as a generator function,
which yields in the middle. The generator yields an object providing details of
the HTTP request it wishes to be sent, ceding control to "something else, I care not
what" which executes the actual web request, and sends an object representing the response
back into the generator. The generator then processes the response.

Here's a toy API client for [The Internet Chuck Norris Database](http://www.icndb.com/).

<script src="https://gitlab.com/samfrances/async-agnostic-api-client-example/snippets/1729032.js"></script>

I still haven't decided if this is a good strategy overall, although it
certainly seems to achieve its immediate goal of allowing a large chunk of
code to be shared between sync and async clients. Comments welcome.

¡Hasta pronto!

#!/usr/bin/env python

import responder

api = responder.API()

@api.route("/{greeting}")
async def greet_world(req, resp, *, greeting):
    resp.text = f"{greeting}, world!"

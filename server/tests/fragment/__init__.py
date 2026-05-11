"""

Fragment is a class that implements calls to fragment, no matter the session

fragment - has multiple rest clients, set beforehand

it has all fragment logic endpoints.
(it does not matter whether randomly selects session)

ton connect - just gives the ton connect data, needed only for the each client
rest client - sends requests with right data, one for each session
auth happens on the rest client

session manager - gets tied to the api client, manages loading and saving the session (only that)

each client i will probably init by itself beforehand (somewhere)

and the fragment class i init inside the lifetime

"""

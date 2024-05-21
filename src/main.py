"""
This module defines the `main()` coroutine for the Apify Actor, executed from the `__main__.py` file.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

# Facebook SDK - library for accessing Facebook Graph API, read more at https://facebook-sdk.readthedocs.io/en/latest/
import facebook

# Apify SDK - toolkit for building Apify Actors, read more at https://docs.apify.com/sdk/python
from apify import Actor


async def main() -> None:
    """
    The main coroutine is being executed using `asyncio.run()`, so do not attempt to make a normal function
    out of it, it will not work. Asynchronous execution is required for communication with Apify platform,
    and it also enhances performance in the field of web scraping significantly.
    """
    async with Actor:
        # Structure of input is defined in input_schema.json
        actor_input = await Actor.get_input() or {}
        search_query = actor_input.get('search_query')
        access_token = actor_input.get('access_token')

        # Initialize the Facebook Graph API client
        graph = facebook.GraphAPI(access_token=access_token)

        # Search for posts related to the search_query
        search_results = graph.search(type='post', q=search_query, fields='message,comments,likes.summary(true),shares')

        # Extract posts, comments, and other engagements
        extracted_data = []
        for post in search_results['data']:
            post_data = {
                'id': post['id'],
                'message': post.get('message'),
                'comments': [comment['message'] for comment in post.get('comments', {}).get('data', [])],
                'likes_count': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                'shares_count': post.get('shares', {}).get('count', 0)
            }
            Actor.log.info(f'Extracted post data: {post_data}')
            extracted_data.append(post_data)

        # Save extracted data to Dataset - a table-like storage
        await Actor.push_data(extracted_data)


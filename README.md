# Getting to Philosophy
''Clicking on the first link in the main text of a Wikipedia article, and then repeating the process for subsequent articles, will usually lead to the Philosophy article. As of February 2016, 97% of all articles in Wikipedia eventually lead to the article Philosophy.
The remaining articles lead to an article without any outgoing wikilinks, to pages that do not exist, or get stuck in loops[...](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)''

# GOAL 
Write a program using Python that performs the following:
* Take any random article on Wikipedia (example: http://en.wikipedia.org/wiki/Art) and click on the first link on the main body of the article that is not within parenthesis or italicized; If you repeat this process for each subsequent article you will often end up on the Philosophy page.

Questions:
* What percentage of pages often lead to philosophy?
* Using the random article link (found on any wikipedia article in the left sidebar),what is the distribution of path lengths for 500 pages, discarding those paths that never reach the Philosophy page?
* How can you reduce the number of http requests necessary for 500 random starting pages?

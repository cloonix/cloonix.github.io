+++
title = 'Working with Hugo Themes (Part 1)'
date = 2024-07-17T18:32:58Z
tags = ['hugo', 'git', 'howto', 'development' ]
categories = ['howto']
type = "blog"
series = ['hugo']
+++

I'm the kind of person who cares a lot about having a good looking theme for my blog before I even start creating content.  

In my first days of a new blogging life with Hugo, I looked at some simple themes. And simple is what Hugo is all about, isn't it? My first theme was [Bear Cub](https://clente.github.io/hugo-bearcub/). Nice and simple, but it lacked something special. I found [bacardi55's theme](https://bacardi55.io), a (smol fork), and liked it a lot. After modifying it a bit to my liking, I ended up using [smol](https://github.com/colorchestra/smol) and forked it. I added this theme as a git submodule. I found this to be the easiest way to work with themes.  

But how do you work with a forked theme in Hugo? Because the workflow seems to be complicated:  

_The (imo) bad way..._  

1. Update forked theme (changing the CSS, templates, etc.)
2. Push changes
3. Fetch/pull theme (submodule) changes in Hugo environment
4. Test it, fix it, go back to Step 1
5. Push the updated submodule in the Hugo enviroment

The simplest CSS changes caused several commit/pushes in my repositories. This development loop was painful. Although it does not happen very often.

The solution is so simple that I got a bit angry and used this loop for a few hours.

Just start the hugo binary with the option `--themesDir ~/path/to/themes`! In the folder `themes` is a sub-folder with my themes:

```shell
hugo server --themesDir ~/git/themes -D
```

It's so easy. :man_facepalming:  

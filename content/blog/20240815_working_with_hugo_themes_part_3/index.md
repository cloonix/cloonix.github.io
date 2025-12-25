---
title: "Working with Hugo (Part 3): Images"
date: "2024-08-15T17:32:58Z"
tags:
  - hugo
  - git
  - howto
  - development
categories:
  - howto
type: blog
series:
  - hugo
---
**TL;DR** ▶️ Long story short, I couldn't find a simple solution to handle images in Hugo's default Markdown parser.

At the time of writing this post, i'm not using a single image in one of my posts.  

The official documentation is quite clear about image processing in a template [[1](https://gohugo.io/content-management/image-processing/)]. But i wonder, how to process a image from Markdown code? In my scenario i want to use use page resources (images bundled with pages). Out of the box you can create a sub-folder in your content directory and put a `index.md` and the picture `filename.jpg` into it. In the markdown code you use:

```md
![Image name](filename.jpg)
```

But this way, there is no option to resize the picture. And standard Markdown has no option to manipulate pictures.  

Some time ago i looked into AsciiDoc [[2](https://asciidoc.org/)]. AsciiDoc is a lightweight markup language for writing technical documentation. It has many more features than Markdown, but is also more complex to use. Inserting an image while resizing it looks like this in AsciiDoc:  

```txt
image::filename.jpg[Image name,200,100]
```

Although it looked promising, I decided not to use AsciiDoc because it would have added another layer of complexity to my blog, which I want to keep as simple as possible. This also means that I will be using the standard markdown way of inserting images and preparing the images before inserting them.  

Do you have a simple solution for that? Write me on [Mastodon](https://chaos.social/@cloonix/) or [Matrix](https://matrix.to/#/@cloonix:matrix.org).

## Links  

[1] <https://gohugo.io/content-management/image-processing/>  
[2] <https://asciidoc.org/>  

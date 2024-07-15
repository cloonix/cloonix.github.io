+++
title = 'A new beginning with Hugo'
date = 2024-07-15T18:30:00Z
author = 'Claus Malter'
tags = ['hugo', 'linux', 'development', 'howto', 'markdown']
categories = ['howto']
series = ['hugo']
+++

## My first steps with Hugo

While installing and building a site with Hugo is not rocket science, I wanted to share some notes on my first steps. Maybe this will become a series.

You need 5 things before you can run Hugo. In my trials, brew.sh was the easiest way to install the prerequisites on Linux.  

## Installation

The installation steps are mostly taken from the officially Hugo documentation at [gohugo.io](https://gohugo.io).  

### git

Use the package manager for your distribution:

```sh
sudo apt install git
```

### go

Go is an open-source programming language developed by Google. It is designed to be efficient, simple, and reliable, making it suitable for a wide range of applications. You need go for hugo.  

For linux there a pre-built binaries:

```sh
cd ~
mkdir tmp
cd tmp
wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
tar xzf go1.22.2.linux-amd64.tar.gz
echo 'export PATH=$PATH:~/go/bin' >> ~/.profile
source ~/.profile
```

### brew.sh

[brew.sh](https://brew.sh) is a package manager for macOS and Linux operating systems. It allows you to easily install and manage various software packages and libraries on your system.

Brew provides a installation script:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Pay attention to the instructions after the installation has finished! There is a command to add the new binaries to your `PATH` variable and other hints. You may need to install a necessary package (including `gcc`) for the next steps (in Debian/Ubuntu).

```sh
sudo apt install build-essential
```

### Dart Sass

Dart Sass is a popular implementation of the Sass (Syntactically Awesome Style Sheets) language. It is a CSS preprocessor that extends the capabilities of CSS, allowing you to write more maintainable and modular stylesheets.  

To install Dart Sass, you can use the following command:

```sh
brew install sass/sass/sass
```

### Finally Hugo

```sh
brew install hugo
```

## Create a site

Creating a site is easy as well. The hard part - at least for me - comes later, when you try to adapt a theme to your needs and create a site structure. But first things first:

```sh
hugo new site quickstart
cd quickstart
git init
git submodule add \
 https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
echo "theme = 'ananke'" >> hugo.toml
hugo server -D
```

You can visit your newly created site at <http://localhost:1313/>. You can vscode or ssh to tunnel your browser to this port. Changing the site will automatically refresh your browser, which makes it very convenient to develop a Hugo site. 

Create a new content with:

```sh
hugo new content content/posts/my-first-post.md
```

You can edit the newly created file and see the updates directly in your browser. Note the `-D` switch when running `hugo server`. It means that drafts will also be displayed. While Hugo uses Markdown out of the box, there is a part at the top of the new page called **Front Matter**. Here you can configure some parts - depending on your theme - of your newly created page. Also the `draft = true` value.

## What's coming next?

Next time i will add some notes regarding the following topics:

- Things I wish I'd known before I started using Hugo
- Adding and customising a theme
- Deploying a Hugo site
- Using github pages to host the site and automatically build the site using github actions.

## Interesting links

- [Hugo Themes](https://themes.gohugo.io/)
- [My favorite theme "Bear Cub"](https://github.com/clente/hugo-bearcub)
- [Markdown Cheat Sheet](https://www.markdownguide.org/cheat-sheet/)

## Closing words

For more information on Hugo and its usage, you can refer to the [official Hugo documentation](https://gohugo.io/documentation/).

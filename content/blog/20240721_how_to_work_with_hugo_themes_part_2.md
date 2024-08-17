+++
title = 'Working with Hugo Themes (Part 2)'
tags = ['hugo', 'git', 'howto', 'development', 'go' ]
categories = ['howto']
date = 2024-07-20T17:52:47Z
type = "blog"
series = ['hugo']
+++

I was not happy with my local development workflow, which I described a few days ago [[1]]({{< ref "#links" >}}), for one reason: The git submodule was inconvenient. After editing and testing my theme, I still had to push the new submodule reference to github, where the github actions workflow would build and deploy the new theme.  

What I wanted was for the github actions script to pull the latest commit of my theme on each build and deploy process. This was actually possible with a submodule, but I had to change a few things in the workflow configuration:

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    submodules: recursive
    ref: 'main'
    # This
    fetch-depth: 0
```  

and  

```yaml
# added the git submodule update line
run: |
    git submodule update --remote --merge \
    && hugo \
    --minify \
    --baseURL "${{ steps.pages.outputs.base_url }}/"
```  

## The "better" way

But what really met my needs was the use of Hugo modules in combination with a workspace (which allows local development). So here is the (hopefully) final setup of my Hugo development and content editing:

First, I added the module (aka theme) to my Hugo configuration:

```toml
[module]
  [[module.imports]]
    path = "github.com/user/theme"
```

Second, i initialize my Hugo folder as a module:

```sh
hugo mod init github.com/<your_username>/<your_project>
```

Third, i get a reference to the latest version of my module(s):

```sh
hugo mod get
```

Now, the hugo build process is pulling the module(s). But only the specific commit when you added the module. You can update the reference with `hugo mod get -u`. And push your Hugo site afterwards.

But we are not finished yet.

## Now the interestig part

Hugo supports workspaces since version v0.109.0 [[2]]({{< ref "#links" >}}). You create a workspace file (e.g. `dev.work`) in your Hugo repository folder with this content:

```sh
go 1.22.2

use .
use ../themes/<yourthemename>
```

... and you set a environment variable or start your `hugo server` process with that variable:

```sh
export HUGO_MODULE_WORKSPACE=./dev.work
```

or

```sh
HUGO_MODULE_WORKSPACE=./dev.work hugo server -D
```

Now Hugo will build the static pages on base of your local theme. But one final step is missing; the build process for github pages. The build file usually is in `.github/workflows/hugo.yml`.

Update the build process for github pages (in the jobs section).

```yaml
run: |
    hugo mod get -u \
    && hugo \
    --minify \
```

Now, with every git commit/push to your Hugo repository, GitHub will automatically pull the latest commit of your theme module and use it to deploy your site.

## Links {#links}  

[1] [Working with Hugo Themes (Part 1)]({{< ref 20240718_how_to_work_with_hugo_themes_part_1.md >}})  
[2] [Module workspaces](https://gohugo.io/hugo-modules/use-modules/#module-workspaces)  

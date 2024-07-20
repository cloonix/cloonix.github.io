+++
title = 'Working with Hugo Themes (Part 2)'
tags = ['hugo', 'git', 'howto', 'development', 'go' ]
categories = ['howto']
date = 2024-07-20T17:52:47Z
draft = true
+++

I was not happy with my local development workflow, which I described a few days ago [1], for one reason: The git submodule was inconvenient. After editing and testing my theme, I still had to push the new submodule reference to github, where the github actions workflow would build and deploy the new theme.  

What I wanted was for the github actions script to pull the updated theme on each build and deploy process. Actually this was possible with a submodule, but I had to change things in the actions configuration:

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

## The "right" way

But what really met my needs was using Hugo modules in combination with a workspace (which allows local development). So here is the (hopefully) final setup of my Hugo development and content editing:

First, i added the module (aka theme) in my Hugo configuration:

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

Now, the hugo build process is pulling the modules. But only the specific commit when you added the module. You can update the reference with `hugo mod get -u`.

```sh
export HUGO_MODULE_WORKSPACE=./dev.work
```

```file
go 1.22.2

use .
use ../themes/smo
```

Update the build process for github pages (`.github/workflows/hugo.yml`)

```yaml
run: |
    hugo mod get -u \
    && hugo \
    --minify \

[1] [Working with Hugo Themes (Part 1)]({{< ref 20240718_how_to_work_with_hugo_themes_part_1.md >}})  

---
title: Markdown test
---

# Markdown test

From https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

### Headers

# H1

Example content under a H1 header

## H2

Example content under a H2 header

### H3

Example content under a H3 header

#### H4

Example content under a H4 header

##### H5

Example content under a H5 header

###### H6

Example content under a H6 header

Alternatively, for H1 and H2, an underline-ish style:

Alt-H1
======

Alt-H2
------

### Emphasis

Emphasis, aka italics, with *asterisks* or _underscores_.

Strong emphasis, aka bold, with **asterisks** or __underscores__.

Combined emphasis with **asterisks and _underscores_**.

Strikethrough uses two tildes. ~~Scratch this.~~

~subscript~ uses one tilde

### Lists

1. First ordered list item
2. Another item
  * Unordered sub-list.
1. Actual numbers don't matter, just that it's a number
    1. Ordered sub-list
4. And another item.

    You can have properly indented paragraphs within list items. Notice the blank line above, and the leading spaces (at least one, but we'll use three here to also align the raw Markdown).

    To have a line break without a paragraph, you will need to use two trailing spaces.
    Note that this line is separate, but within the same paragraph.
    (This is contrary to the typical GFM line break behaviour, where trailing spaces are not required.)

* Unordered list can use asterisks
- Or minuses
+ Or pluses

this is some words in a paragraph

* this
* is
* a
* list


### Links

[I'm an inline-style link](https://www.google.com)

[I'm an inline-style link with title](https://www.google.com "Google's Homepage")

[I'm a reference-style link][Arbitrary case-insensitive reference text]

[I'm a relative reference to a repository file](../blob/master/LICENSE)

[You can use numbers for reference-style link definitions][1]

Or leave it empty and use the [link text itself].

URLs and URLs in angle brackets will automatically get turned into links.
http://www.example.com or <http://www.example.com> and sometimes
example.com (but not on Github, for example).

Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org
[1]: http://slashdot.org
[link text itself]: http://www.reddit.com

### Images

Here's our logo (hover to see the title text):

Inline-style:
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

Reference-style:
![alt text][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2"

### Code

Inline `code` has `back-ticks around` it.

```javascript
var s = "JavaScript syntax highlighting";
alert(s);
```

```python
s = "Python syntax highlighting"
print s
```

```
No language indicated, so no syntax highlighting.
But let's throw in a <b>tag</b>.
```

### Tables

Colons can be used to align columns.

| Tables        | Are           | Cool  |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |

There must be at least 3 dashes separating each header cell.
The outer pipes (|) are optional, and you don't need to make the
raw Markdown line up prettily. You can also use inline Markdown.

Markdown | Less | Pretty
--- | --- | ---
*Still* | `renders` | **nicely**
1 | 2 | 3

| This | Is a bigger table |
| - | - |
| `The_content` | should wrap over multiple lines because I'm really just running my mouth spouting bullshit right now. Like why are you even reading this, its clearly not helpful. Lorem ipsum. |

### Blockquotes

> Blockquotes are very handy in email to emulate reply text.
> This line is part of the same quote.

Quote break.

> This is a very long line that will still be quoted properly when it wraps. Oh boy let's keep writing to make sure this is long enough to actually wrap for everyone. Oh, you can *put* **Markdown** into a blockquote.

break

> > > This is a quote

> > in a quote

> in another quote

### Inline HTML

<dl>
  <dt>Definition list</dt>
  <dd>Is something people use sometimes.</dd>

  <dt>Markdown in HTML</dt>
  <dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>
</dl>

### Horizontal rule

Three or more...

---

Hyphens

***

Asterisks

___

Underscores

### Line breaks

Here's a line for us to start with.

This line is separated from the one above by two newlines, so it will be a *separate paragraph*.

This line is also a separate paragraph, but...
This line is only separated by a single newline, so it's a separate line in the *same paragraph*.

### Emjoi

Raw unicode emoji 👍

short name :+1:

[More emoji](/emoji_test.html)


### Line wrap

20 characters Lorem
40 characters Lorem ipsum dolor sit ame
60 characters Lorem ipsum dolor sit amet, consectetur adipi
80 characters Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitu
100 characters Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur fermentum nisl ne

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur fermentum nisl neque, et dapibus ex condimentum ut. Morbi et neque tincidunt, dignissim justo quis, rutrum quam. Vivamus nec risus est. In eget imperdiet lacus. Quisque tempor tellus lacus, sit amet ullamcorper justo pharetra eget. Donec molestie sapien sed leo eleifend tristique ut at arcu. Sed eu ligula ex. Duis hendrerit felis a eros placera

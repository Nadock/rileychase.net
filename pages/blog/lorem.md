---
type: debug
title: Test post, please ignore
subtitle: If you're seeing this, no you're not.
description: dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua
date: 2022-12-14
tags:
  - test
  - lorem
  - blog
---

## Lorem ipsum

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Scelerisque varius morbi enim nunc faucibus a pellentesque sit amet. Ante in nibh mauris cursus mattis molestie a. Convallis posuere morbi leo urna molestie at. Ante metus dictum at tempor commodo ullamcorper a lacus. Semper auctor neque vitae tempus quam pellentesque. Eget duis at tellus at urna condimentum. Arcu odio ut sem nulla pharetra. Id faucibus nisl tincidunt eget nullam non nisi est. Hac habitasse platea dictumst quisque sagittis purus sit amet. Sed velit dignissim sodales ut eu sem integer. Posuere urna nec tincidunt praesent semper feugiat nibh sed. Venenatis lectus magna fringilla urna. Donec massa sapien faucibus et molestie ac. Quis auctor elit sed vulputate mi sit amet. Magna sit amet purus gravida quis. Netus et malesuada fames ac turpis. Urna cursus eget nunc scelerisque viverra mauris in aliquam sem.

## Elementum sagittis

Elementum sagittis vitae et leo duis ut diam quam nulla. In cursus turpis massa tincidunt dui ut. Sit amet dictum sit amet. Vehicula ipsum a arcu cursus vitae congue mauris rhoncus aenean. Sodales neque sodales ut etiam sit amet nisl purus. At auctor urna nunc id cursus. Cursus eget nunc scelerisque viverra. Duis tristique sollicitudin nibh sit amet commodo nulla. Quisque egestas diam in arcu cursus euismod quis viverra nibh. Metus vulputate eu scelerisque felis imperdiet proin fermentum leo vel. Enim sit amet venenatis urna cursus. Cras pulvinar mattis nunc sed blandit libero volutpat. Sem nulla pharetra diam sit amet nisl suscipit. Lectus urna duis convallis convallis tellus. Auctor urna nunc id cursus metus aliquam eleifend mi in. Ultricies integer quis auctor elit sed vulputate mi sit amet.

## Eu augue ut

Eu augue ut lectus arcu bibendum at. Maecenas pharetra convallis posuere morbi leo urna. Sed id semper risus in hendrerit. Nisl nunc mi ipsum faucibus. Arcu cursus vitae congue mauris rhoncus aenean vel elit scelerisque. Ut enim blandit volutpat maecenas volutpat. Scelerisque mauris pellentesque pulvinar pellentesque. Amet purus gravida quis blandit turpis. Massa massa ultricies mi quis. Morbi enim nunc faucibus a pellentesque. Tortor id aliquet lectus proin. Imperdiet proin fermentum leo vel orci porta non.
Eget aliquet nibh praesent tristique magna sit amet. Lacus suspendisse faucibus interdum posuere lorem ipsum dolor sit. Sociis natoque penatibus et magnis dis. Fermentum leo vel orci porta. Ac odio tempor orci dapibus ultrices in iaculis nunc sed. Quisque id diam vel quam elementum pulvinar. Volutpat diam ut venenatis tellus.

Ultricies tristique nulla aliquet enim tortor. Odio ut enim blandit volutpat maecenas volutpat blandit. Sit amet dictum sit amet justo donec. Vulputate dignissim suspendisse in est ante in nibh mauris cursus. Ornare arcu dui vivamus arcu felis bibendum ut tristique et. Erat nam at lectus urna duis convallis convallis. Odio pellentesque diam volutpat commodo sed egestas egestas fringilla phasellus.
Aliquam ultrices sagittis orci a. Mi sit amet mauris commodo quis imperdiet massa tincidunt nunc. Tellus integer feugiat scelerisque varius morbi. Elit ut aliquam purus sit amet luctus venenatis lectus. Rhoncus urna neque viverra justo nec ultrices. Sociis natoque penatibus et magnis dis.

```python
def _format_runtime(t_0: int, t_1: int) -> str:
    """
    Format the elapsed time between two nanosecond time readings from `time.time_ns`.
    """
    t_detla = abs(t_0 - t_1) / (10 ** 9)
    if t_detla < 0.001:
        return "under 1ms"

    return f"{t_detla:.3f}s"
```

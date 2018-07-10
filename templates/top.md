{%- set ns = namespace(rank=1) -%}
Top 10 @ {{server_name}}
```
{%- for player in top_ten -%}
    {%- if player.rating != top_ten[loop.index-2].rating -%}
        {%- set ns.rank = loop.index -%}
    {%- endif -%}
{{ "%2s" | format(ns.rank,) }}. {{ "%12s" | format(player.name) }} | {{ player.rating | int }}
{% endfor -%}
```
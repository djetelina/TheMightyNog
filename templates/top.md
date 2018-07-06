{%- set rank = 1 -%}
Top 10 @ {{server_name}}
```
{%- for player in top_ten -%}
    {%- if player.rating != top_ten[loop.index-2].rating -%}
        {%- set rank = loop.index -%}
    {%- endif -%}
{{ "%2s" | format(rank,) }}. {{ "%12s" | format(player.name) }} | {{ player.rating | int }}
{% endfor -%}
```
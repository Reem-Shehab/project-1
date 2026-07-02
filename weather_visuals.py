"""
Animated weather scenes for the Streamlit app (app.py only).

weather_animation(condition) returns a self-contained HTML string (pure HTML+CSS,
no external resources) that is rendered in an isolated iframe. One animated scene
per condition: Sunny (glowing sun + rotating ray ring + drifting clouds),
Rainy (bobbing clouds + parallax rain), Cloudy (drifting volumetric clouds),
Snowy (falling, spinning snowflakes). Unknown condition -> a plain sky gradient.
"""
import random


def weather_animation(condition, height=220):
    """Return a self-contained HTML string with an animated CSS scene for the
    given weather condition. condition is one of: 'Sunny','Rainy','Cloudy','Snowy'."""
    H = int(height)
    FALL = H + 60  # px fall distance so motion scales with the passed height

    # Stable, per-condition seed (deterministic across process restarts).
    seeds = {'Sunny': 11, 'Rainy': 23, 'Cloudy': 37, 'Snowy': 53}
    rng = random.Random(seeds.get(condition, 7))

    # Each condition gets its own multi-stop sky gradient so it reads as weather.
    skies = {
        'Sunny':  'linear-gradient(180deg,#2f8fdb 0%,#5aa7e6 38%,#a9dcff 74%,#ffe6b0 100%)',
        'Rainy':  'linear-gradient(180deg,#3a4653 0%,#55636f 55%,#7d8b98 100%)',
        'Cloudy': 'linear-gradient(180deg,#6f8caa 0%,#9db6cf 52%,#d8e6f2 100%)',
        'Snowy':  'linear-gradient(180deg,#7c93b2 0%,#b6cde3 52%,#eef7fd 100%)',
    }
    sky = skies.get(condition, 'linear-gradient(180deg,#6fa0cf 0%,#d3e6f6 100%)')

    # ---- particle / shape builders (loops concatenate inline-styled divs) ----
    def volu_cloud(left, top, scale, dur, opacity, color, delay):
        # Soft volumetric cloud: four overlapping blurred blobs.
        return ('<div class="cloud" style="left:{l:.0f}%;top:{t:.0f}%;--k:{s:.2f};'
                'opacity:{o:.2f};--cc:{c};animation-duration:{d:.1f}s;'
                'animation-delay:{dl:.1f}s;"><i></i><i></i><i></i><i></i></div>'
                ).format(l=left, t=top, s=scale, o=opacity, c=color, d=dur, dl=delay)

    def bob_cloud(left, top, scale, opacity, color, period):
        # A cloud that gently bobs in place (for rain/snow scenes).
        return ('<div class="cloud" style="left:{l:.0f}%;top:{t:.0f}%;--k:{s:.2f};'
                'opacity:{o:.2f};--cc:{c};animation:bob {p:.1f}s ease-in-out infinite;">'
                '<i></i><i></i><i></i><i></i></div>'
                ).format(l=left, t=top, s=scale, o=opacity, c=color, p=period)

    def rain_layers(bands):
        html = ''
        for (count, op, dur_base, w) in bands:
            spans = ''
            for _ in range(count):
                spans += ('<span style="left:{l:.1f}%;height:{h:.0f}px;width:{w:.1f}px;'
                          'opacity:{o:.2f};animation-duration:{d:.2f}s;'
                          'animation-delay:-{dl:.2f}s;"></span>'
                          ).format(l=rng.uniform(-2, 100), h=rng.uniform(12, 22), w=w,
                                   o=op, d=dur_base + rng.uniform(-0.1, 0.15),
                                   dl=rng.uniform(0, 3))
            html += '<div class="rain">' + spans + '</div>'
        return html

    def snow_layers(bands):
        html = ''
        for (count, op, dur_base, size) in bands:
            spans = ''
            for _ in range(count):
                dur = dur_base + rng.uniform(-1.2, 1.6)
                spans += ('<span class="flake" style="left:{l:.1f}%;opacity:{o:.2f};'
                          'animation-duration:{d:.2f}s;animation-delay:-{dl:.2f}s;">'
                          '<i style="width:{s:.1f}px;height:{s:.1f}px;--sw:{sw:.0f}px;'
                          'animation-duration:{sd:.2f}s;animation-delay:-{sdl:.2f}s;"></i>'
                          '</span>'
                          ).format(l=rng.uniform(0, 100), o=op, d=dur, dl=rng.uniform(0, dur),
                                   s=size + rng.uniform(-0.8, 1.2), sw=rng.uniform(12, 34),
                                   sd=rng.uniform(2.2, 3.8), sdl=rng.uniform(0, 3))
            html += '<div class="snow">' + spans + '</div>'
        return html

    # ---- per-condition scene content ----
    if condition == 'Sunny':
        scene = ('<div class="sun-wrap"><div class="rays"></div>'
                 '<div class="glow"></div><div class="sun"></div></div>'
                 + volu_cloud(6, 62, 0.85, 46, 0.55, 'rgba(255,255,255,.9)', -4)
                 + volu_cloud(60, 74, 1.05, 60, 0.4, 'rgba(255,250,235,.85)', -22))
    elif condition == 'Rainy':
        scene = (bob_cloud(6, 6, 1.3, 0.97, 'rgba(224,231,238,.98)', 4.5)
                 + bob_cloud(46, 2, 1.55, 0.95, 'rgba(202,211,222,.98)', 5.2)
                 + rain_layers([(24, 0.35, 1.0, 1.6), (24, 0.55, 0.78, 2.0),
                                (22, 0.8, 0.58, 2.6)]))
    elif condition == 'Cloudy':
        scene = (volu_cloud(-8, 16, 1.0, 42, 0.6, 'rgba(255,255,255,.8)', -4)
                 + volu_cloud(28, 36, 1.35, 58, 0.9, 'rgba(255,255,255,.97)', -16)
                 + volu_cloud(66, 8, 1.15, 50, 0.8, 'rgba(240,246,252,.92)', -30)
                 + volu_cloud(12, 58, 1.6, 72, 0.72, 'rgba(255,255,255,.82)', -8)
                 + volu_cloud(80, 46, 0.8, 36, 0.65, 'rgba(255,255,255,.78)', -40))
    elif condition == 'Snowy':
        scene = (bob_cloud(8, 4, 1.2, 0.6, 'rgba(255,255,255,.75)', 5.0)
                 + snow_layers([(20, 0.55, 8.5, 4.5), (20, 0.78, 6.5, 6.0),
                                (18, 1.0, 4.8, 7.5)]))
    else:
        scene = ''  # unknown -> plain sky (gradient only)

    # ---- CSS: plain (non-f) string with __TOKEN__ placeholders. Literal
    #      braces never collide with Python formatting. ----
    css = """
    *{margin:0;padding:0;box-sizing:border-box}
    html,body{height:100%;background:transparent}
    .stage{position:relative;width:100%;height:__H__px;overflow:hidden;border-radius:16px;
      background:__SKY__;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
      box-shadow:inset 0 -28px 55px rgba(0,0,0,.16),inset 0 18px 38px rgba(255,255,255,.10)}

    /* volumetric clouds: four overlapping blurred blobs */
    .cloud{position:absolute;width:120px;height:44px;will-change:transform;
      animation:drift linear infinite}
    .cloud i{position:absolute;bottom:0;background:var(--cc,#fff);border-radius:50%;
      filter:blur(3px)}
    .cloud i:nth-child(1){left:4px;width:52px;height:52px}
    .cloud i:nth-child(2){left:32px;width:76px;height:76px;bottom:-8px}
    .cloud i:nth-child(3){left:74px;width:56px;height:56px}
    .cloud i:nth-child(4){left:18px;width:98px;height:30px;bottom:-2px;border-radius:30px}
    @keyframes drift{from{transform:translateX(-140px) scale(var(--k,1))}
      to{transform:translateX(calc(100vw + 140px)) scale(var(--k,1))}}
    @keyframes bob{0%,100%{transform:scale(var(--k,1)) translateY(0)}
      50%{transform:scale(var(--k,1)) translateY(-7px)}}

    /* layered sun: blurred glow + gradient disc + rotating masked ray ring */
    .sun-wrap{position:absolute;top:-40px;right:-34px;width:210px;height:210px;
      animation:sunbob 5s ease-in-out infinite}
    .sun{position:absolute;inset:66px;border-radius:50%;
      background:radial-gradient(circle at 38% 34%,#fffef4 0%,#ffe680 45%,#ffbf3c 100%);
      box-shadow:0 0 28px 8px rgba(255,205,90,.85),0 0 66px 24px rgba(255,180,60,.45);
      animation:pulse 4s ease-in-out infinite}
    .glow{position:absolute;inset:38px;border-radius:50%;filter:blur(14px);
      background:radial-gradient(circle,rgba(255,224,150,.85),rgba(255,200,90,0) 68%);
      animation:pulse 4s ease-in-out infinite}
    .rays{position:absolute;inset:-12px;border-radius:50%;
      background:repeating-conic-gradient(from 0deg,rgba(255,244,200,.6) 0deg 5deg,
        transparent 5deg 17deg);
      -webkit-mask:radial-gradient(circle,transparent 43%,#000 46%,#000 60%,transparent 72%);
      mask:radial-gradient(circle,transparent 43%,#000 46%,#000 60%,transparent 72%);
      animation:spin 26s linear infinite}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes pulse{0%,100%{transform:scale(1);opacity:.95}50%{transform:scale(1.06);opacity:1}}
    @keyframes sunbob{0%,100%{transform:translateY(0)}50%{transform:translateY(6px)}}

    /* rain: parallax bands of bright, slanted streaks */
    .rain{position:absolute;inset:0}
    .rain span{position:absolute;top:-16%;border-radius:2px;
      background:linear-gradient(rgba(210,232,255,0),rgba(224,240,255,.95));
      transform:rotate(12deg);will-change:transform;animation:fall linear infinite}
    @keyframes fall{from{transform:translateY(-40px) rotate(12deg)}
      to{transform:translateY(__FALL__px) rotate(12deg)}}

    /* snow: falling wrapper + inner spinning/swaying flake */
    .snow{position:absolute;inset:0}
    .flake{position:absolute;top:-8%;will-change:transform;animation:snowfall linear infinite}
    .flake i{display:block;border-radius:50%;
      background:radial-gradient(circle at 35% 30%,#fff,#dcebf8);
      box-shadow:0 0 6px rgba(255,255,255,.9);animation:sway ease-in-out infinite}
    @keyframes snowfall{from{transform:translateY(-40px)}to{transform:translateY(__FALL__px)}}
    @keyframes sway{0%,100%{transform:translateX(calc(var(--sw,10px) * -1)) rotate(0)}
      50%{transform:translateX(var(--sw,10px)) rotate(200deg)}}

    @media (prefers-reduced-motion:reduce){.stage *{animation:none!important}}
    """
    css = (css.replace('__H__', str(H))
              .replace('__SKY__', sky)
              .replace('__FALL__', str(FALL)))

    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + css +
            '</style></head><body><div class="stage">' + scene + '</div></body></html>')

"""
Generalized single-location weekly report template.

This reproduces the layout used for Salateira weekly reports
(hero + KPI cards + WoW comparison + daily dynamics + top dishes +
ops metrics + ratings/reviews), parameterized by partner branding
so it works for any partner registered in partners_config.py.
"""

import math

UAH = 42.0

CSS = """*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#F8F9FA;color:#1A1A1A;line-height:1.6;max-width:900px;margin:0 auto;padding:0 0 40px;}
.hero{color:white;padding:28px 28px 22px;position:relative;overflow:hidden;}
.hero::before{content:"";position:absolute;top:-50px;right:-50px;width:260px;height:260px;background:radial-gradient(circle,rgba(255,255,255,.08) 0%,transparent 70%);border-radius:50%;}
.badge{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;padding:3px 10px;border-radius:4px;margin-bottom:10px;}
.hero h1{font-size:20px;font-weight:800;line-height:1.2;margin-bottom:4px;}
.hero-sub{font-size:12px;color:rgba(255,255,255,.5);margin-bottom:14px;}
.kpis{display:flex;gap:16px;flex-wrap:wrap;}
.kpi{font-size:11px;color:rgba(255,255,255,.4);}
.kpi strong{display:block;font-size:18px;font-weight:700;color:white;margin-bottom:1px;}
.wrap{padding:0 18px;}
.sec{padding:18px 0 0;}
.sec-t{font-size:14px;font-weight:700;margin-bottom:3px;}
.sec-s{font-size:11px;color:#6B7280;margin-bottom:8px;}
.hr{height:1px;background:#E8E8E8;margin:0 0 10px;}
.card{background:white;border-radius:10px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);}
.cl{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;}
.cv{font-size:20px;font-weight:800;margin-bottom:2px;}
.cd{font-size:11px;color:#9CA3AF;}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.g2{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;}
@media(max-width:580px){.g4,.g3,.g2{grid-template-columns:1fr 1fr;}}
.day-row{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-top:6px;}
.day-cell{border-radius:7px;padding:6px 3px;text-align:center;border-top:3px solid #2AAF6D;background:white;box-shadow:0 1px 3px rgba(0,0,0,.05);}
.dn{font-size:8px;color:#9CA3AF;margin-bottom:1px;}
.dv{font-size:14px;font-weight:800;}
.dg{font-size:9px;color:#9CA3AF;margin-top:1px;}
.pb{height:4px;background:#EBEBEB;border-radius:2px;overflow:hidden;margin-top:2px;}
.pf{height:100%;border-radius:2px;}
.dish-row{display:flex;align-items:center;gap:8px;margin-bottom:5px;}
.rv{background:white;border-radius:8px;padding:10px;box-shadow:0 1px 4px rgba(0,0,0,.05);margin-bottom:6px;}
.rv.neg{border-left:3px solid #EF4444;}
.rv.pos{border-left:3px solid #2AAF6D;}
.footer{background:#0d2a1a;color:rgba(255,255,255,.3);text-align:center;padding:14px;font-size:10px;margin-top:24px;}"""


def sf(v, d=0):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return d
    return v


def fmt(n):
    try:
        return f"{int(round(float(n))):,}".replace(",", "\u00a0")
    except Exception:
        return "0"


def wow_span(pct):
    if pct is None:
        return ""
    c = "#EF4444" if pct < 0 else "#34D186"
    a = "▼" if pct < 0 else "▲"
    return f'<span style="color:{c};font-size:10px;font-weight:700;">{a}{abs(pct):.1f}%</span>'


def avail_color(v):
    if v >= 0.95:
        return "#34D186"
    if v >= 0.90:
        return "#F59E0B"
    return "#EF4444"


def rat_color(r):
    if r is None:
        return "#9CA3AF"
    if r >= 4.7:
        return "#34D186"
    if r >= 4.4:
        return "#F59E0B"
    return "#EF4444"


def build_report(
    *,
    pid,
    name,
    brand_label,
    partner_emoji,
    city,
    period_label,
    period_short,
    prev_label,
    days_ua,
    days_iso,
    cur_row,
    prev_row,
    delivered_total,
    prev_delivered_total,
    daily_map,
    dishes,
    rating_row,
    comments_pos,
    comments_neg,
):
    c = cur_row
    delivered = int(sf(delivered_total, 0))
    failed = int(sf(c.get("failed", 0)))
    gmv = round(sf(c.get("gmv_eur", 0)) * UAH)
    bolt_promo = round(sf(c.get("bolt_promo", 0)) * UAH)
    promo_ord = int(sf(c.get("promo_ord", 0)))
    bp_ord = int(sf(c.get("bp_ord", 0)))
    new_u = int(sf(c.get("new_u", 0)))
    prep_min = round(sf(c.get("prep_min", 0)), 1)
    accept_min = round(sf(c.get("accept_min", 0)), 2)
    avail = sf(c.get("avail", 0))
    bad_rt = sf(c.get("bad_rt", 0))
    aov = round(gmv / max(delivered, 1))
    bp_sh = round(bp_ord / max(delivered, 1) * 100)
    promo_sh = round(promo_ord / max(delivered, 1) * 100)
    bad_orders = int(round(bad_rt * delivered)) if bad_rt else 0
    bad_pct = round(bad_rt * 100, 1)

    prev_del = int(sf(prev_delivered_total, 0))
    prev_gmv = round(sf(prev_row.get("gmv_eur", 0)) * UAH)
    wow_ord = round((delivered - prev_del) / prev_del * 100, 1) if prev_del else None
    wow_gmv = round((gmv - prev_gmv) / prev_gmv * 100, 1) if prev_gmv else None

    avg_rat = sf(rating_row.get("avg_rating"), None)
    review_cnt = int(sf(rating_row.get("review_cnt", 0)))
    bad_cnt = int(sf(rating_row.get("bad_cnt", 0)))
    week_rat = avg_rat if (avg_rat and review_cnt) else (sf(c.get("rating"), None) or None)
    rt_c = rat_color(week_rat)
    rt_str = f"{week_rat:.2f} ★" if week_rat else "—"
    r_bad_pct = round(bad_cnt / max(review_cnt, 1) * 100, 1) if review_cnt else 0.0

    daily = [daily_map.get(dd, 0) for dd in days_iso]
    peak = max(daily) if daily else 0
    cells = ""
    for i in range(7):
        w = int(daily[i] / peak * 100) if peak else 0
        cells += (
            f'<div class="day-cell" style="border-top-color:#2AAF6D;">'
            f'<div class="dn">{days_ua[i]}</div>'
            f'<div class="dv" style="color:#2AAF6D;">{daily[i]}</div>'
            f'<div class="pb"><div class="pf" style="width:{w}%;background:#2AAF6D;"></div></div>'
            f"</div>"
        )

    if dishes:
        dishes_html = "".join(
            f'<div style="font-size:11px;color:#374151;padding:4px 0;border-bottom:1px solid #F3F4F6;">{partner_emoji} {d}</div>'
            for d in dishes
        )
    else:
        dishes_html = '<div style="font-size:11px;color:#9CA3AF;">Даних по стравах немає</div>'

    avail_pct = round(avail * 100, 1)
    avc = avail_color(avail)
    prep_c = "#34D186" if prep_min <= 15 else ("#F59E0B" if prep_min <= 20 else "#EF4444")
    prep_note = "Ціль &lt;15 хв ✅" if prep_min <= 15 else "Ціль &lt;15 хв"
    acc_c = "#34D186" if accept_min < 1 else "#F59E0B"
    acc_note = "Ціль &lt;1 хв ✅" if accept_min < 1 else "Ціль &lt;1 хв"
    bad_c = "#34D186" if bad_pct < 10 else "#EF4444"
    cancel_note = "Скасувань не зафіксовано" if failed == 0 else f"Скасовано замовлень: {failed}"

    if comments_pos or comments_neg:
        rev_html = ""
        for rt, cmt in comments_pos:
            rev_html += (
                f'<div class="rv pos"><div style="font-size:11px;color:#F59E0B;margin-bottom:2px;">'
                f'{"★"*rt}{"☆"*(5-rt)} {rt}/5</div>'
                f'<div style="font-size:11px;color:#374151;">«{cmt}»</div></div>'
            )
        for rt, cmt in comments_neg:
            rev_html += (
                f'<div class="rv neg"><div style="font-size:11px;color:#EF4444;margin-bottom:2px;">'
                f'{"★"*rt}{"☆"*(5-rt)} {rt}/5</div>'
                f'<div style="font-size:11px;color:#374151;">«{cmt}»</div></div>'
            )
    else:
        rev_html = '<div style="font-size:11px;color:#9CA3AF;">Текстових відгуків немає</div>'

    wow_hero = f'<div class="kpi"><strong>{wow_span(wow_ord)}</strong>WoW замовлення</div>' if wow_ord is not None else ""

    html = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} · Bolt Food · {period_short} 2026</title>
<style>
{CSS}
</style></head><body>

<div class="hero" style="background:linear-gradient(135deg,#0d2a1a 0%,#1a4d32 100%);">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
    <div style="background:rgba(52,209,134,.15);border:1px solid rgba(52,209,134,.25);border-radius:6px;padding:4px 9px;font-size:10px;font-weight:700;color:#2AAF6D;">⚡ Bolt Food Ukraine</div>
    <div style="font-size:12px;color:rgba(255,255,255,.2);">×</div>
    <div style="background:rgba(42,175,109,.15);border:1px solid rgba(42,175,109,.3);border-radius:6px;padding:4px 9px;font-size:10px;font-weight:700;color:#2AAF6D;">{partner_emoji} {brand_label}</div>
    <span style="margin-left:auto;background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3);border-radius:4px;padding:2px 8px;font-size:9px;font-weight:700;color:#F59E0B;">ТИЖНЕВИЙ ЗВІТ</span>
  </div>
  <div class="badge" style="background:#2AAF6D;color:#fff;">{period_label}</div>
  <h1>{name}</h1>
  <p class="hero-sub">📍 {city} · ID: {pid} · {period_label}</p>
  <div class="kpis">
    <div class="kpi"><strong>{delivered}</strong>Доставлено</div>
    <div class="kpi"><strong>{fmt(gmv)}&nbsp;₴</strong>Виручка</div>
    <div class="kpi"><strong>{fmt(aov)}&nbsp;₴</strong>AOV</div>
    <div class="kpi"><strong style="color:{rt_c};">{rt_str}</strong>Рейтинг</div>
    {wow_hero}
  </div>
</div>
<div class="wrap">

<div class="sec">
  <div class="sec-t">📊 Показники тижня — {period_label}</div><div class="hr"></div>
  <div style="font-size:10px;color:#9CA3AF;margin-bottom:8px;">* «Доставлено» = усі виконані замовлення (доставка курʼєром + самовивіз), співставно з Looker</div>
  <div class="g4" style="margin-bottom:10px;">
    <div class="card"><div class="cl">Доставлено</div><div class="cv" style="color:#2AAF6D;">{delivered}</div><div class="cd">{wow_span(wow_ord)} vs пр. тиж.</div></div>
    <div class="card"><div class="cl">Виручка ₴</div><div class="cv">{fmt(gmv)}</div><div class="cd">{wow_span(wow_gmv)} vs пр. тиж.</div></div>
    <div class="card"><div class="cl">AOV ₴</div><div class="cv">{fmt(aov)}</div></div>
    <div class="card"><div class="cl">Bolt промо ₴</div><div class="cv" style="color:#2AAF6D;">{fmt(bolt_promo)}</div></div>
  </div>
  <div class="g4">
    <div class="card"><div class="cl">Нових клієнтів</div><div class="cv" style="color:#7C3AED;">{new_u}</div></div>
    <div class="card"><div class="cl">Bolt+ замовл.</div><div class="cv" style="color:#34D186;">{bp_ord}</div><div class="cd">{bp_sh}%</div></div>
    <div class="card"><div class="cl">Промо замовл.</div><div class="cv">{promo_ord}</div><div class="cd">{promo_sh}%</div></div>
    <div class="card"><div class="cl">Bad orders</div><div class="cv" style="color:{bad_c};">{bad_orders}</div><div class="cd">{bad_pct}%</div></div>
  </div>
</div>

<div class="sec">
  <div class="sec-t">📈 WoW порівняння</div><div class="hr"></div>
  <div class="g2">
    <div class="card" style="border-left:3px solid #BFDBFE;background:#EFF6FF;">
      <div style="font-size:10px;font-weight:700;color:#1e40af;text-transform:uppercase;margin-bottom:6px;">📅 Попередній тиж. {prev_label}</div>
      <div style="font-size:11px;color:#374151;">Доставлено: <strong>{prev_del}</strong> · GMV: <strong>{fmt(prev_gmv)}&nbsp;₴</strong></div>
    </div>
    <div class="card" style="border-left:3px solid #BBF7D0;background:#F0FFF8;">
      <div style="font-size:10px;font-weight:700;color:#065F46;text-transform:uppercase;margin-bottom:6px;">📅 Поточний тиж. {period_short} {wow_span(wow_ord)}</div>
      <div style="font-size:11px;color:#374151;">Доставлено: <strong>{delivered}</strong> · GMV: <strong>{fmt(gmv)}&nbsp;₴</strong></div>
      <div style="font-size:10px;color:#6B7280;margin-top:2px;">Нових клієнтів: {new_u} · Bolt+: {bp_ord}</div>
    </div>
  </div>
</div>

<div class="sec">
  <div class="sec-t">📅 Денна динаміка — {period_short}</div><div class="hr"></div>
  <div class="day-row">{cells}</div>
</div>

<div class="sec">
  <div class="sec-t">{partner_emoji} Топ страви тижня</div><div class="hr"></div>
  {dishes_html}
</div>

<div class="sec">
  <div class="sec-t">⚙️ Операційні метрики</div><div class="hr"></div>
  <div class="g3">
    <div class="card"><div class="cl">Доступність</div><div class="cv" style="color:{avc};">{avail_pct}%</div>
      <div class="pb"><div class="pf" style="width:{avail_pct}%;background:{avc};"></div></div></div>
    <div class="card"><div class="cl">Час приготув.</div><div class="cv" style="color:{prep_c};">{prep_min} хв</div><div class="cd">{prep_note}</div></div>
    <div class="card"><div class="cl">Час прийому</div><div class="cv" style="color:{acc_c};">{accept_min} хв</div><div class="cd">{acc_note}</div></div>
  </div>
  <div style="margin-top:8px;"><div style="font-size:11px;color:#9CA3AF;">{cancel_note}</div></div>
</div>

<div class="sec">
  <div class="sec-t">⭐ Рейтинг та відгуки</div><div class="hr"></div>
  <div class="g4" style="margin-bottom:10px;">
    <div class="card" style="border-left:3px solid {rt_c};"><div class="cl">Рейтинг</div><div class="cv" style="color:{rt_c};">{rt_str}</div></div>
    <div class="card"><div class="cl">Оцінок</div><div class="cv">{review_cnt}</div></div>
    <div class="card"><div class="cl">Bad rate</div><div class="cv" style="color:{'#34D186' if r_bad_pct<10 else '#EF4444'};">{r_bad_pct}%</div></div>
    <div class="card"><div class="cl">Промо %</div><div class="cv">{promo_sh}%</div></div>
  </div>
  {rev_html}
</div>

</div>

<div class="footer">Bolt Food Ukraine × {name} · {period_label} · Конфіденційно · ID: {pid}</div>
</body></html>"""
    return html, dict(
        delivered=delivered, gmv=gmv, wow_ord=wow_ord, wow_gmv=wow_gmv,
        rating=week_rat, new_u=new_u,
    )

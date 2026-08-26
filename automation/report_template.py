"""
Generalized single-location weekly report template.

This reproduces the layout used for Salateira weekly reports
(hero + KPI cards + WoW comparison + daily dynamics + top dishes +
ops metrics + ratings/reviews), parameterized by partner branding
so it works for any partner registered in partners_config.py.
"""

import html
import math

UAH = 42.0

# UI copy. Partners default to "uk"; set locale="en" in PARTNERS to switch.
STRINGS = {
    "uk": {
        "html_lang": "uk",
        "weekly_badge": "ТИЖНЕВИЙ ЗВІТ",
        "delivered": "Доставлено",
        "revenue": "Виручка",
        "rating": "Рейтинг",
        "wow_orders": "WoW замовлення",
        "week_metrics": "Показники тижня",
        "delivered_note": "* «Доставлено» = усі виконані замовлення (доставка курʼєром + самовивіз), співставно з Looker",
        "vs_prev": "vs пр. тиж.",
        "revenue_uah": "Виручка ₴",
        "bolt_promo": "Bolt промо ₴",
        "partner_promo": "Партнер промо ₴",
        "promo_total": "Промо разом ₴",
        "promo_uah": "Промо ₴",
        "partner_short": "партнер",
        "promo_note": "Промо-витрати: знижки та доставку фінансують Bolt і партнер окремо, «разом» — сума обох",
        "new_customers": "Нових клієнтів",
        "bolt_plus_orders": "Bolt+ замовл.",
        "promo_orders": "Промо замовл.",
        "wow_comparison": "WoW порівняння",
        "prev_week": "Попередній тиж.",
        "curr_week": "Поточний тиж.",
        "daily_trend": "Денна динаміка",
        "daily_comparison": "Динаміка замовлень за днями",
        "daily_comparison_sub": "Звітний тиждень у порівнянні з попереднім",
        "top_dishes": "Топ страви тижня",
        "no_dishes": "Даних по стравах немає",
        "ops": "Операційні метрики",
        "availability": "Доступність",
        "prep_time": "Час приготув.",
        "accept_time": "Час прийому",
        "min": "хв",
        "target_prep_ok": "Ціль &lt;15 хв ✅",
        "target_prep": "Ціль &lt;15 хв",
        "target_accept_ok": "Ціль &lt;1 хв ✅",
        "target_accept": "Ціль &lt;1 хв",
        "no_cancels": "Скасувань не зафіксовано",
        "cancelled": "Скасовано замовлень: {n}",
        "rating_reviews": "Рейтинг та відгуки",
        "reviews_count": "Оцінок",
        "promo_pct": "Промо %",
        "no_comments": "Текстових відгуків немає",
        "confidential": "Конфіденційно",
        "network_total": "Мережа тотал",
        "summary_network": "ЗВЕДЕНИЙ ЗВІТ · МЕРЕЖА",
        "network_total_title": "{name} — тотал мережі, {n} локацій",
        "active_locations": "Активних локацій",
        "avg_rating": "Сер. рейтинг",
        "network_kpis": "Мережа тотал — ключові показники",
        "compared_prev": "Порівняння з попереднім тижнем",
        "cancelled_short": "Скасовано",
        "avg_availability": "Сер. доступність",
        "network_daily": "Денна динаміка мережі",
        "network_daily_sub": "Сума доставлених замовлень по всіх локаціях, по днях",
        "network_locations": "Локації мережі",
        "click_location": "Клікніть на назву локації, щоб відкрити її детальний тижневий звіт",
        "location": "Локація",
        "onboarding": "онбордінг",
        "network_footer": "Зведений звіт по мережі",
        "network_html_title": "{name} · Мережа тотал · Bolt Food · {period} {year}",
    },
    "en": {
        "html_lang": "en",
        "weekly_badge": "WEEKLY REPORT",
        "delivered": "Delivered",
        "revenue": "Revenue",
        "rating": "Rating",
        "wow_orders": "WoW orders",
        "week_metrics": "Week metrics",
        "delivered_note": "* “Delivered” = all completed orders (courier delivery + pickup), comparable with Looker",
        "vs_prev": "vs prev. week",
        "revenue_uah": "Revenue ₴",
        "bolt_promo": "Bolt promo ₴",
        "partner_promo": "Partner promo ₴",
        "promo_total": "Promo total ₴",
        "promo_uah": "Promo ₴",
        "partner_short": "partner",
        "promo_note": "Promo spend: discounts and delivery are funded by Bolt and the partner separately, “total” is the sum of both",
        "new_customers": "New customers",
        "bolt_plus_orders": "Bolt+ orders",
        "promo_orders": "Promo orders",
        "wow_comparison": "WoW comparison",
        "prev_week": "Previous week",
        "curr_week": "Current week",
        "daily_trend": "Daily trend",
        "daily_comparison": "Daily order trend",
        "daily_comparison_sub": "Reporting week compared with the previous week",
        "top_dishes": "Top dishes this week",
        "no_dishes": "No dish data",
        "ops": "Operations",
        "availability": "Availability",
        "prep_time": "Prep time",
        "accept_time": "Accept time",
        "min": "min",
        "target_prep_ok": "Target &lt;15 min ✅",
        "target_prep": "Target &lt;15 min",
        "target_accept_ok": "Target &lt;1 min ✅",
        "target_accept": "Target &lt;1 min",
        "no_cancels": "No cancellations",
        "cancelled": "Cancelled orders: {n}",
        "rating_reviews": "Rating and reviews",
        "reviews_count": "Reviews",
        "promo_pct": "Promo %",
        "no_comments": "No written reviews",
        "confidential": "Confidential",
        "network_total": "Network total",
        "summary_network": "SUMMARY · NETWORK",
        "network_total_title": "{name} — network total, {n} locations",
        "active_locations": "Active locations",
        "avg_rating": "Avg. rating",
        "network_kpis": "Network total — key metrics",
        "compared_prev": "Compared with previous week",
        "cancelled_short": "Cancelled",
        "avg_availability": "Avg. availability",
        "network_daily": "Network daily trend",
        "network_daily_sub": "Sum of delivered orders across all locations, by day",
        "network_locations": "Network locations",
        "click_location": "Click a location name to open its weekly report",
        "location": "Location",
        "onboarding": "onboarding",
        "network_footer": "Network summary report",
        "network_html_title": "{name} · Network total · Bolt Food · {period} {year}",
    },
}

CSS = """:root{--color-content-action-primary:#2A9C64;--color-content-tertiary:#5F6563;--color-border-separator:#DEE2E1;--color-layer-floor-1:#FFFFFF;}
*{box-sizing:border-box;margin:0;padding:0;}
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
.trend-chart{background:var(--color-layer-floor-1);border-radius:16px;padding:14px 14px 8px;overflow:hidden;}
.trend-chart svg{display:block;width:100%;height:auto;min-height:220px;}
.trend-legend{display:flex;gap:18px;flex-wrap:wrap;margin:0 0 8px;font-size:11px;color:var(--color-content-tertiary);}
.trend-key{display:inline-flex;align-items:center;gap:6px;}
.trend-line{width:22px;height:3px;border-radius:600rem;background:var(--color-content-action-primary);}
.trend-line.prev{height:0;border-top:2px dashed var(--color-content-tertiary);background:none;}
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


def build_daily_comparison_chart(days, current, previous, current_label, previous_label):
    """Responsive inline SVG comparing delivered orders by weekday."""
    width, height = 760, 280
    left, right, top, bottom = 54, 20, 24, 52
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_value = max(current + previous + [1])
    y_max = max(5, int(math.ceil(max_value / 5.0) * 5))

    def point(i, value):
        x = left + (plot_w * i / 6 if len(days) > 1 else plot_w / 2)
        y = top + plot_h * (1 - value / y_max)
        return x, y

    current_points = [point(i, value) for i, value in enumerate(current)]
    previous_points = [point(i, value) for i, value in enumerate(previous)]
    current_polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in current_points)
    previous_polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in previous_points)

    grid = []
    for step in range(5):
        value = round(y_max * step / 4)
        y = top + plot_h * (1 - step / 4)
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
            'stroke="var(--color-border-separator)" stroke-width="1"/>'
            f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" '
            f'fill="var(--color-content-tertiary)" font-size="10">{value}</text>'
        )

    x_labels = []
    point_marks = []
    for i, label in enumerate(days):
        x, _ = current_points[i]
        day_name = str(label).split("<br>", 1)[0]
        x_labels.append(
            f'<text x="{x:.1f}" y="{height-18}" text-anchor="middle" '
            'fill="var(--color-content-tertiary)" font-size="11">'
            f"{html.escape(day_name)}</text>"
        )
        cx, cy = current_points[i]
        px, py = previous_points[i]
        point_marks.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="var(--color-layer-floor-1)" '
            'stroke="var(--color-content-tertiary)" stroke-width="2"/>'
            f'<text x="{px:.1f}" y="{min(height-bottom-5, py+17):.1f}" text-anchor="middle" '
            'fill="var(--color-content-tertiary)" font-size="10">'
            f"{previous[i]}</text>"
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="var(--color-content-action-primary)"/>'
            f'<text x="{cx:.1f}" y="{max(top+10, cy-9):.1f}" text-anchor="middle" '
            'fill="var(--color-content-action-primary)" font-size="10" font-weight="700">'
            f"{current[i]}</text>"
        )

    return (
        '<div class="trend-chart">'
        '<div class="trend-legend">'
        f'<span class="trend-key"><span class="trend-line"></span>{html.escape(current_label)}</span>'
        f'<span class="trend-key"><span class="trend-line prev"></span>{html.escape(previous_label)}</span>'
        '</div>'
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{html.escape(current_label)} vs {html.escape(previous_label)}">'
        + "".join(grid)
        + f'<polyline points="{previous_polyline}" fill="none" stroke="var(--color-content-tertiary)" '
          'stroke-width="2.5" stroke-dasharray="7 6" stroke-linecap="round" stroke-linejoin="round"/>'
        + f'<polyline points="{current_polyline}" fill="none" stroke="var(--color-content-action-primary)" '
          'stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
        + "".join(point_marks)
        + "".join(x_labels)
        + "</svg></div>"
    )


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
    prev_daily_map=None,
    show_daily_comparison_chart=False,
    dishes,
    rating_row,
    comments_pos,
    comments_neg,
    locale="uk",
):
    s = STRINGS.get(locale) or STRINGS["uk"]
    c = cur_row
    delivered = int(sf(delivered_total, 0))
    failed = int(sf(c.get("failed", 0)))
    gmv = round(sf(c.get("gmv_eur", 0)) * UAH)
    bolt_promo = round(sf(c.get("bolt_promo", 0)) * UAH)
    part_promo = round(sf(c.get("part_promo", 0)) * UAH)
    promo_total = bolt_promo + part_promo
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
    previous_daily = []
    if prev_daily_map:
        previous_daily = [prev_daily_map.get(i, 0) for i in range(7)]
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

    comparison_chart_html = ""
    if show_daily_comparison_chart:
        comparison_chart_html = f"""
<div class="sec">
  <div class="sec-t">{s['daily_comparison']}</div>
  <div class="sec-s">{s['daily_comparison_sub']}</div><div class="hr"></div>
  {build_daily_comparison_chart(
      days_ua,
      daily,
      previous_daily or [0] * 7,
      f"{s['curr_week']} {period_short}",
      f"{s['prev_week']} {prev_label}",
  )}
</div>"""

    if dishes:
        dishes_html = "".join(
            f'<div style="font-size:11px;color:#374151;padding:4px 0;border-bottom:1px solid #F3F4F6;">{partner_emoji} {d}</div>'
            for d in dishes
        )
    else:
        dishes_html = '<div style="font-size:11px;color:#9CA3AF;">' + s["no_dishes"] + "</div>"

    avail_pct = round(avail * 100, 1)
    avc = avail_color(avail)
    prep_c = "#34D186" if prep_min <= 15 else ("#F59E0B" if prep_min <= 20 else "#EF4444")
    prep_note = s["target_prep_ok"] if prep_min <= 15 else s["target_prep"]
    acc_c = "#34D186" if accept_min < 1 else "#F59E0B"
    acc_note = s["target_accept_ok"] if accept_min < 1 else s["target_accept"]
    bad_c = "#34D186" if bad_pct < 10 else "#EF4444"
    cancel_note = s["no_cancels"] if failed == 0 else s["cancelled"].format(n=failed)

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
        rev_html = '<div style="font-size:11px;color:#9CA3AF;">' + s["no_comments"] + "</div>"

    wow_hero = f'<div class="kpi"><strong>{wow_span(wow_ord)}</strong>{s["wow_orders"]}</div>' if wow_ord is not None else ""

    html = f"""<!DOCTYPE html>
<html lang="{s['html_lang']}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} · Bolt Food · {period_short} 2026</title>
<style>
{CSS}
</style></head><body>

<div class="hero" style="background:linear-gradient(135deg,#0d2a1a 0%,#1a4d32 100%);">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
    <div style="background:rgba(52,209,134,.15);border:1px solid rgba(52,209,134,.25);border-radius:6px;padding:4px 9px;font-size:10px;font-weight:700;color:#2AAF6D;">⚡ Bolt Food Ukraine</div>
    <div style="font-size:12px;color:rgba(255,255,255,.2);">×</div>
    <div style="background:rgba(42,175,109,.15);border:1px solid rgba(42,175,109,.3);border-radius:6px;padding:4px 9px;font-size:10px;font-weight:700;color:#2AAF6D;">{partner_emoji} {brand_label}</div>
    <span style="margin-left:auto;background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3);border-radius:4px;padding:2px 8px;font-size:9px;font-weight:700;color:#F59E0B;">{s['weekly_badge']}</span>
  </div>
  <div class="badge" style="background:#2AAF6D;color:#fff;">{period_label}</div>
  <h1>{name}</h1>
  <p class="hero-sub">📍 {city} · ID: {pid} · {period_label}</p>
  <div class="kpis">
    <div class="kpi"><strong>{delivered}</strong>{s['delivered']}</div>
    <div class="kpi"><strong>{fmt(gmv)}&nbsp;₴</strong>{s['revenue']}</div>
    <div class="kpi"><strong>{fmt(aov)}&nbsp;₴</strong>AOV</div>
    <div class="kpi"><strong style="color:{rt_c};">{rt_str}</strong>{s['rating']}</div>
    {wow_hero}
  </div>
</div>
<div class="wrap">

<div class="sec">
  <div class="sec-t">📊 {s['week_metrics']} — {period_label}</div><div class="hr"></div>
  <div style="font-size:10px;color:#9CA3AF;margin-bottom:8px;">{s['delivered_note']}</div>
  <div class="g4" style="margin-bottom:10px;">
    <div class="card"><div class="cl">{s['delivered']}</div><div class="cv" style="color:#2AAF6D;">{delivered}</div><div class="cd">{wow_span(wow_ord)} {s['vs_prev']}</div></div>
    <div class="card"><div class="cl">{s['revenue_uah']}</div><div class="cv">{fmt(gmv)}</div><div class="cd">{wow_span(wow_gmv)} {s['vs_prev']}</div></div>
    <div class="card"><div class="cl">AOV ₴</div><div class="cv">{fmt(aov)}</div></div>
    <div class="card"><div class="cl">{s['promo_orders']}</div><div class="cv">{promo_ord}</div><div class="cd">{promo_sh}%</div></div>
  </div>
  <div class="g3" style="margin-bottom:10px;">
    <div class="card"><div class="cl">{s['bolt_promo']}</div><div class="cv" style="color:#2AAF6D;">{fmt(bolt_promo)}</div></div>
    <div class="card"><div class="cl">{s['partner_promo']}</div><div class="cv" style="color:#F59E0B;">{fmt(part_promo)}</div></div>
    <div class="card"><div class="cl">{s['promo_total']}</div><div class="cv">{fmt(promo_total)}</div></div>
  </div>
  <div style="font-size:10px;color:#9CA3AF;margin-bottom:10px;">{s['promo_note']}</div>
  <div class="g3">
    <div class="card"><div class="cl">{s['new_customers']}</div><div class="cv" style="color:#7C3AED;">{new_u}</div></div>
    <div class="card"><div class="cl">{s['bolt_plus_orders']}</div><div class="cv" style="color:#34D186;">{bp_ord}</div><div class="cd">{bp_sh}%</div></div>
    <div class="card"><div class="cl">Bad orders</div><div class="cv" style="color:{bad_c};">{bad_orders}</div><div class="cd">{bad_pct}%</div></div>
  </div>
</div>

<div class="sec">
  <div class="sec-t">📈 {s['wow_comparison']}</div><div class="hr"></div>
  <div class="g2">
    <div class="card" style="border-left:3px solid #BFDBFE;background:#EFF6FF;">
      <div style="font-size:10px;font-weight:700;color:#1e40af;text-transform:uppercase;margin-bottom:6px;">📅 {s['prev_week']} {prev_label}</div>
      <div style="font-size:11px;color:#374151;">{s['delivered']}: <strong>{prev_del}</strong> · GMV: <strong>{fmt(prev_gmv)}&nbsp;₴</strong></div>
    </div>
    <div class="card" style="border-left:3px solid #BBF7D0;background:#F0FFF8;">
      <div style="font-size:10px;font-weight:700;color:#065F46;text-transform:uppercase;margin-bottom:6px;">📅 {s['curr_week']} {period_short} {wow_span(wow_ord)}</div>
      <div style="font-size:11px;color:#374151;">{s['delivered']}: <strong>{delivered}</strong> · GMV: <strong>{fmt(gmv)}&nbsp;₴</strong></div>
      <div style="font-size:10px;color:#6B7280;margin-top:2px;">{s['new_customers']}: {new_u} · Bolt+: {bp_ord}</div>
    </div>
  </div>
</div>

<div class="sec">
  <div class="sec-t">📅 {s['daily_trend']} — {period_short}</div><div class="hr"></div>
  <div class="day-row">{cells}</div>
</div>

{comparison_chart_html}

<div class="sec">
  <div class="sec-t">{partner_emoji} {s['top_dishes']}</div><div class="hr"></div>
  {dishes_html}
</div>

<div class="sec">
  <div class="sec-t">⚙️ {s['ops']}</div><div class="hr"></div>
  <div class="g3">
    <div class="card"><div class="cl">{s['availability']}</div><div class="cv" style="color:{avc};">{avail_pct}%</div>
      <div class="pb"><div class="pf" style="width:{avail_pct}%;background:{avc};"></div></div></div>
    <div class="card"><div class="cl">{s['prep_time']}</div><div class="cv" style="color:{prep_c};">{prep_min} {s['min']}</div><div class="cd">{prep_note}</div></div>
    <div class="card"><div class="cl">{s['accept_time']}</div><div class="cv" style="color:{acc_c};">{accept_min} {s['min']}</div><div class="cd">{acc_note}</div></div>
  </div>
  <div style="margin-top:8px;"><div style="font-size:11px;color:#9CA3AF;">{cancel_note}</div></div>
</div>

<div class="sec">
  <div class="sec-t">⭐ {s['rating_reviews']}</div><div class="hr"></div>
  <div class="g4" style="margin-bottom:10px;">
    <div class="card" style="border-left:3px solid {rt_c};"><div class="cl">{s['rating']}</div><div class="cv" style="color:{rt_c};">{rt_str}</div></div>
    <div class="card"><div class="cl">{s['reviews_count']}</div><div class="cv">{review_cnt}</div></div>
    <div class="card"><div class="cl">Bad rate</div><div class="cv" style="color:{'#34D186' if r_bad_pct<10 else '#EF4444'};">{r_bad_pct}%</div></div>
    <div class="card"><div class="cl">{s['promo_pct']}</div><div class="cv">{promo_sh}%</div></div>
  </div>
  {rev_html}
</div>

</div>

<div class="footer">Bolt Food Ukraine × {name} · {period_label} · {s['confidential']} · ID: {pid}</div>
</body></html>"""
    return html, dict(
        delivered=delivered, gmv=gmv, wow_ord=wow_ord, wow_gmv=wow_gmv,
        rating=week_rat, new_u=new_u, avail=avail, bp_ord=bp_ord,
        promo_ord=promo_ord, bolt_promo=bolt_promo, part_promo=part_promo,
        promo_total=promo_total, bad_orders=bad_orders,
        review_cnt=review_cnt, bad_cnt=bad_cnt, failed=failed,
        prev_delivered=prev_del, prev_gmv=prev_gmv, daily=daily,
        previous_daily=previous_daily,
    )


NETWORK_CSS = """:root{--color-content-action-primary:#2A9C64;--color-content-tertiary:#5F6563;--color-border-separator:#DEE2E1;--color-layer-floor-1:#FFFFFF;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#F8F9FA;color:#1A1A1A;line-height:1.6;max-width:1100px;margin:0 auto;padding:0 0 40px;}
.hero{color:white;padding:36px 36px 28px;position:relative;overflow:hidden;}
.hero::before{content:"";position:absolute;top:-60px;right:-60px;width:300px;height:300px;background:radial-gradient(circle,rgba(255,255,255,.1) 0%,transparent 70%);border-radius:50%;}
.badge{display:inline-block;font-size:11px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;padding:4px 12px;border-radius:4px;margin-bottom:12px;}
.hero h1{font-size:26px;font-weight:800;line-height:1.2;margin-bottom:6px;}
.hero-sub{font-size:13px;color:rgba(255,255,255,.55);margin-bottom:18px;}
.kpis{display:flex;gap:20px;flex-wrap:wrap;}
.kpi{font-size:12px;color:rgba(255,255,255,.4);}
.kpi strong{display:block;font-size:22px;font-weight:700;color:white;margin-bottom:1px;}
.wrap{padding:0 26px;}
.sec{padding:28px 0 0;}
.sec-t{font-size:17px;font-weight:700;margin-bottom:4px;}
.sec-s{font-size:12px;color:#6B7280;margin-bottom:14px;}
.hr{height:1px;background:#E8E8E8;margin:0 0 16px;}
.card{background:white;border-radius:11px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.06);}
.cl{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px;}
.cv{font-size:23px;font-weight:800;margin-bottom:2px;}
.cd{font-size:11px;color:#9CA3AF;}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.g6{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;}
@media(max-width:900px){.g4,.g6{grid-template-columns:repeat(2,1fr);}}
table{width:100%;border-collapse:collapse;font-size:13px;}
th{background:#F8F9FA;padding:8px 11px;text-align:left;font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid #E8E8E8;}
td{padding:8px 11px;border-bottom:1px solid #F3F4F6;vertical-align:middle;}
tr:hover td{background:#FAFAFA;}
.num{text-align:right;}
.b{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;}
.bg{background:rgba(52,209,134,.15);color:#16a057;}
.bo{background:rgba(245,158,11,.15);color:#b46309;}
.br{background:rgba(239,68,68,.15);color:#dc2626;}
.pb{height:5px;background:#E8E8E8;border-radius:3px;overflow:hidden;margin-top:3px;}
.pf{height:100%;border-radius:3px;}
.dish-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.footer{background:#0d2a1a;color:rgba(255,255,255,.3);text-align:center;padding:16px;font-size:11px;margin-top:28px;}
a.loclink{color:inherit;text-decoration:none;font-weight:600;}
a.loclink:hover{text-decoration:underline;}
.trend-chart{background:var(--color-layer-floor-1);border-radius:16px;padding:14px 14px 8px;overflow:hidden;}
.trend-chart svg{display:block;width:100%;height:auto;min-height:220px;}
.trend-legend{display:flex;gap:18px;flex-wrap:wrap;margin:0 0 8px;font-size:11px;color:var(--color-content-tertiary);}
.trend-key{display:inline-flex;align-items:center;gap:6px;}
.trend-line{width:22px;height:3px;border-radius:600rem;background:var(--color-content-action-primary);}
.trend-line.prev{height:0;border-top:2px dashed var(--color-content-tertiary);background:none;}"""


def build_network_summary(
    *,
    display_name,
    emoji,
    brand_color,
    period_label,
    period_short,
    prev_label,
    days_ua,
    days_iso,
    loc_results,
    show_daily_comparison_chart=False,
    locale="uk",
):
    """loc_results: list of dicts with keys pid, name, short_name, city, fname, stats (from build_report)."""
    s = STRINGS.get(locale) or STRINGS["uk"]
    n_loc = len(loc_results)
    net_delivered = sum(r["stats"]["delivered"] for r in loc_results)
    net_gmv = sum(r["stats"]["gmv"] for r in loc_results)
    net_prev_del = sum(r["stats"]["prev_delivered"] for r in loc_results)
    net_prev_gmv = sum(r["stats"]["prev_gmv"] for r in loc_results)
    net_bolt_promo = sum(r["stats"]["bolt_promo"] for r in loc_results)
    net_part_promo = sum(r["stats"].get("part_promo", 0) for r in loc_results)
    net_promo_total = net_bolt_promo + net_part_promo
    net_promo_ord = sum(r["stats"]["promo_ord"] for r in loc_results)
    net_bp_ord = sum(r["stats"]["bp_ord"] for r in loc_results)
    net_new_u = sum(r["stats"]["new_u"] for r in loc_results)
    net_failed = sum(r["stats"]["failed"] for r in loc_results)
    net_bad_orders = sum(r["stats"]["bad_orders"] for r in loc_results)
    rated = [r["stats"]["rating"] for r in loc_results if r["stats"]["rating"]]
    net_rating = sum(rated) / len(rated) if rated else None
    avails = [r["stats"]["avail"] for r in loc_results if r["stats"].get("avail")]
    net_avail = sum(avails) / len(avails) if avails else 0
    active_loc = sum(1 for r in loc_results if r["stats"]["delivered"] > 0)

    net_aov = round(net_gmv / max(net_delivered, 1))
    wow_ord = round((net_delivered - net_prev_del) / net_prev_del * 100, 1) if net_prev_del else None
    wow_gmv = round((net_gmv - net_prev_gmv) / net_prev_gmv * 100, 1) if net_prev_gmv else None
    promo_sh = round(net_promo_ord / max(net_delivered, 1) * 100)
    bp_sh = round(net_bp_ord / max(net_delivered, 1) * 100)

    # Network daily dynamics (sum of per-location daily arrays, aligned to days_iso)
    net_daily = [0] * len(days_iso)
    net_previous_daily = [0] * len(days_iso)
    for r in loc_results:
        daily = r["stats"].get("daily") or []
        previous_daily = r["stats"].get("previous_daily") or []
        for i in range(min(len(daily), len(net_daily))):
            net_daily[i] += daily[i]
        for i in range(min(len(previous_daily), len(net_previous_daily))):
            net_previous_daily[i] += previous_daily[i]
    peak = max(net_daily) if net_daily else 0
    day_cells = ""
    for i in range(len(days_iso)):
        w = int(net_daily[i] / peak * 100) if peak else 0
        day_cells += (
            f'<div style="text-align:center;background:white;border-radius:8px;padding:8px 4px;border-top:3px solid {brand_color};box-shadow:0 1px 4px rgba(0,0,0,.05);">'
            f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">{days_ua[i]}</div>'
            f'<div style="font-size:16px;font-weight:800;color:{brand_color};">{net_daily[i]}</div>'
            f'<div class="pb"><div class="pf" style="width:{w}%;background:{brand_color};"></div></div>'
            f"</div>"
        )

    network_comparison_chart_html = ""
    if show_daily_comparison_chart:
        network_comparison_chart_html = f"""
<div class="sec">
  <div class="sec-t">{s['daily_comparison']}</div>
  <div class="sec-s">{s['daily_comparison_sub']}</div><div class="hr"></div>
  {build_daily_comparison_chart(
      days_ua,
      net_daily,
      net_previous_daily,
      f"{s['curr_week']} {period_short}",
      f"{s['prev_week']} {prev_label}",
  )}
</div>"""

    # Location breakdown table, sorted by delivered desc
    rows_sorted = sorted(loc_results, key=lambda r: -r["stats"]["delivered"])
    loc_rows = ""
    for r in rows_sorted:
        st = r["stats"]
        rc = rat_color(st["rating"])
        rt_str = f'{st["rating"]:.2f}&nbsp;★' if st["rating"] else "—"
        onb = f'<span class="b bo" style="margin-left:6px;">{s["onboarding"]}</span>' if st["delivered"] == 0 else ""
        loc_rows += (
            f'<tr><td><a class="loclink" href="{r["fname"]}">{r["short_name"]}</a>{onb}<br>'
            f'<span style="font-size:10px;color:#9CA3AF;">ID {r["pid"]} · {r["city"]}</span></td>'
            f'<td class="num"><strong>{fmt(st["delivered"])}</strong> {wow_span(st["wow_ord"])}</td>'
            f'<td class="num">{fmt(st["gmv"])}&nbsp;₴</td>'
            f'<td class="num"><span style="color:{rc};font-weight:700;">{rt_str}</span></td>'
            f'<td class="num">{fmt(st.get("promo_total", st["bolt_promo"]))}&nbsp;₴<br>'
            f'<span style="font-size:9px;color:#9CA3AF;">Bolt {fmt(st["bolt_promo"])} · '
            f'{s["partner_short"]} {fmt(st.get("part_promo", 0))}</span></td>'
            f'<td class="num">{fmt(st["bp_ord"])}</td>'
            f'<td class="num">{round(st["avail"]*100,1) if st.get("avail") else "—"}%</td>'
            f"</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="{s['html_lang']}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{s['network_html_title'].format(name=display_name, period=period_short, year=2026)}</title>
<style>
{NETWORK_CSS}
</style></head><body>

<div class="hero" style="background:linear-gradient(135deg,#0d2a1a 0%,#1a4d32 100%);">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap;">
    <div style="background:rgba(52,209,134,.15);border:1px solid rgba(52,209,134,.25);border-radius:6px;padding:5px 11px;font-size:11px;font-weight:700;color:#2AAF6D;">⚡ Bolt Food Ukraine</div>
    <div style="font-size:13px;color:rgba(255,255,255,.2);">×</div>
    <div style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);border-radius:6px;padding:5px 11px;font-size:11px;font-weight:700;color:{brand_color};">{emoji} {display_name}</div>
    <span style="margin-left:auto;background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3);border-radius:4px;padding:3px 9px;font-size:10px;font-weight:700;color:#F59E0B;">{s['summary_network']}</span>
  </div>
  <div class="badge" style="background:{brand_color};color:#1A1A1A;">{period_label}</div>
  <h1>{s['network_total_title'].format(name=display_name, n=n_loc)}</h1>
  <p class="hero-sub">{s['active_locations']}: {active_loc}/{n_loc} · {period_label}</p>
  <div class="kpis">
    <div class="kpi"><strong>{fmt(net_delivered)}</strong>{s['delivered']} {wow_span(wow_ord)}</div>
    <div class="kpi"><strong>{fmt(net_gmv)}&nbsp;₴</strong>{s['revenue']} {wow_span(wow_gmv)}</div>
    <div class="kpi"><strong>{fmt(net_aov)}&nbsp;₴</strong>AOV</div>
    <div class="kpi"><strong style="color:{rat_color(net_rating)};">{f'{net_rating:.2f} ★' if net_rating else '—'}</strong>{s['avg_rating']}</div>
    <div class="kpi"><strong>{fmt(net_new_u)}</strong>{s['new_customers']}</div>
  </div>
</div>
<div class="wrap">

<div class="sec">
  <div class="sec-t">📊 {s['network_kpis']}, {period_label}</div>
  <div class="sec-s">{s['compared_prev']}: {prev_label}</div><div class="hr"></div>
  <div class="g6" style="margin-bottom:14px;">
    <div class="card"><div class="cl">{s['delivered']}</div><div class="cv" style="color:{brand_color};">{fmt(net_delivered)}</div><div class="cd">{wow_span(wow_ord)} {s['vs_prev']}</div></div>
    <div class="card"><div class="cl">{s['revenue_uah']}</div><div class="cv">{fmt(net_gmv)}</div><div class="cd">{wow_span(wow_gmv)}</div></div>
    <div class="card"><div class="cl">AOV ₴</div><div class="cv">{fmt(net_aov)}</div></div>
    <div class="card"><div class="cl">{s['bolt_promo']}</div><div class="cv" style="color:#2AAF6D;">{fmt(net_bolt_promo)}</div></div>
    <div class="card"><div class="cl">{s['partner_promo']}</div><div class="cv" style="color:#F59E0B;">{fmt(net_part_promo)}</div></div>
    <div class="card"><div class="cl">{s['promo_total']}</div><div class="cv">{fmt(net_promo_total)}</div></div>
  </div>
  <div class="g6">
    <div class="card"><div class="cl">{s['bolt_plus_orders']}</div><div class="cv" style="color:#34D186;">{fmt(net_bp_ord)}</div><div class="cd">{bp_sh}%</div></div>
    <div class="card"><div class="cl">{s['promo_orders']}</div><div class="cv">{fmt(net_promo_ord)}</div><div class="cd">{promo_sh}%</div></div>
    <div class="card"><div class="cl">{s['new_customers']}</div><div class="cv" style="color:#7C3AED;">{fmt(net_new_u)}</div></div>
    <div class="card"><div class="cl">{s['cancelled_short']}</div><div class="cv" style="color:{'#EF4444' if net_failed else '#9CA3AF'};">{fmt(net_failed)}</div></div>
    <div class="card"><div class="cl">Bad orders</div><div class="cv" style="color:{'#34D186' if net_bad_orders==0 else '#EF4444'};">{fmt(net_bad_orders)}</div></div>
    <div class="card"><div class="cl">{s['avg_availability']}</div><div class="cv" style="color:{avail_color(net_avail)};">{round(net_avail*100,1)}%</div></div>
  </div>
  <div style="font-size:11px;color:#9CA3AF;margin-top:12px;">{s['promo_note']}</div>
</div>

<div class="sec">
  <div class="sec-t">📅 {s['network_daily']} — {period_short}</div>
  <div class="sec-s">{s['network_daily_sub']}</div><div class="hr"></div>
  <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:8px;">{day_cells}</div>
</div>

{network_comparison_chart_html}

<div class="sec">
  <div class="sec-t">📍 {s['network_locations']} — {period_label}</div>
  <div class="sec-s">{s['click_location']}</div><div class="hr"></div>
  <div style="overflow-x:auto;">
  <table><thead><tr>
    <th>{s['location']}</th><th class="num">{s['delivered']}</th><th class="num">{s['revenue_uah']}</th>
    <th class="num">{s['rating']}</th><th class="num">{s['promo_uah']}</th>
    <th class="num">Bolt+</th><th class="num">{s['availability']}</th>
  </tr></thead><tbody>
    {loc_rows}
  </tbody></table>
  </div>
</div>

</div>
<div class="footer">Bolt Food Ukraine × {display_name} · {s['network_footer']} · {period_label} · {s['confidential']}</div>
</body></html>"""
    return html, dict(delivered=net_delivered, gmv=net_gmv, rating=net_rating)

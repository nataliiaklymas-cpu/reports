"""Weekly reviews report: location, rating, comment, order code, datetime, amount."""

import html
import math
from datetime import datetime

from report_template import rat_color, fmt


STRINGS = {
    "uk": {
        "html_lang": "uk",
        "badge": "ВІДГУКИ МЕРЕЖІ",
        "title_network": "{name} — відгуки мережі",
        "title_location": "{name}",
        "reviews": "Відгуки",
        "ratings": "Оцінок",
        "with_comment": "З коментарем",
        "avg": "Сер. оцінка",
        "order_code": "Код замовлення",
        "order_dt": "Дата й час замовлення",
        "order_value": "Вартість",
        "no_comment": "Без коментаря",
        "no_reviews": "За цей тиждень оцінок немає",
        "confidential": "Конфіденційно",
        "html_title_net": "{name} · Відгуки мережі · Bolt Food · {period}",
        "html_title_loc": "{name} · Відгуки · Bolt Food · {period}",
        "footer_net": "Відгуки мережі",
        "footer_loc": "Відгуки локації",
    },
    "en": {
        "html_lang": "en",
        "badge": "NETWORK REVIEWS",
        "title_network": "{name} — network reviews",
        "title_location": "{name}",
        "reviews": "Reviews",
        "ratings": "Ratings",
        "with_comment": "With comment",
        "avg": "Avg. rating",
        "order_code": "Order code",
        "order_dt": "Order date and time",
        "order_value": "Order value",
        "no_comment": "No comment",
        "no_reviews": "No ratings this week",
        "confidential": "Confidential",
        "html_title_net": "{name} · Network reviews · Bolt Food · {period}",
        "html_title_loc": "{name} · Reviews · Bolt Food · {period}",
        "footer_net": "Network reviews",
        "footer_loc": "Location reviews",
    },
}

CSS = """*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#F8F9FA;color:#1A1A1A;line-height:1.6;max-width:900px;margin:0 auto;padding:0 0 40px;}
.hero{color:white;padding:28px 28px 22px;position:relative;overflow:hidden;background:linear-gradient(135deg,#0d2a1a 0%,#1a4d32 100%);}
.hero::before{content:"";position:absolute;top:-50px;right:-50px;width:260px;height:260px;background:radial-gradient(circle,rgba(255,255,255,.08) 0%,transparent 70%);border-radius:50%;}
.badge{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;padding:3px 10px;border-radius:4px;margin-bottom:10px;background:#2AAF6D;color:#fff;}
.hero h1{font-size:20px;font-weight:800;line-height:1.2;margin-bottom:4px;}
.hero-sub{font-size:12px;color:rgba(255,255,255,.5);margin-bottom:14px;}
.kpis{display:flex;gap:16px;flex-wrap:wrap;}
.kpi{font-size:11px;color:rgba(255,255,255,.4);}
.kpi strong{display:block;font-size:18px;font-weight:700;color:white;margin-bottom:1px;}
.wrap{padding:0 18px;}
.sec{padding:18px 0 0;}
.sec-t{font-size:14px;font-weight:700;margin-bottom:8px;}
.hr{height:1px;background:#E8E8E8;margin:0 0 12px;}
.rv{background:white;border-radius:10px;padding:14px 16px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:10px;}
.rv.neg{border-left:3px solid #EF4444;}
.rv.mid{border-left:3px solid #F59E0B;}
.rv.pos{border-left:3px solid #2AAF6D;}
.loc{font-size:13px;font-weight:700;margin-bottom:4px;}
.stars{font-size:12px;margin-bottom:6px;font-feature-settings:"tnum";}
.cmt{font-size:14px;color:#374151;margin-bottom:10px;}
.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
@media(max-width:580px){.meta{grid-template-columns:1fr;}}
.ml{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.7px;}
.mv{font-size:13px;font-weight:650;font-feature-settings:"tnum";}
.footer{background:#0d2a1a;color:rgba(255,255,255,.3);text-align:center;padding:14px;font-size:10px;margin-top:24px;}
.empty{font-size:13px;color:#9CA3AF;padding:12px 0;}"""


def _sf(v, default=None):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    return v


def format_order_dt(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    if hasattr(value, "strftime"):
        return value.strftime("%d.%m.%Y %H:%M")
    text = str(value).strip()
    if not text or text.lower() == "nat" or text.lower() == "nan":
        return "—"
    for fmt_in in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt_in).strftime("%d.%m.%Y %H:%M")
        except ValueError:
            continue
    return text[:16].replace("T", " ")


def _review_cards(reviews, s):
    if not reviews:
        return f'<div class="empty">{s["no_reviews"]}</div>'
    parts = []
    for rev in reviews:
        rating = int(_sf(rev.get("rating"), 0) or 0)
        tone = "pos" if rating >= 4 else ("neg" if rating <= 2 else "mid")
        rc = rat_color(float(rating) if rating else None)
        comment = (str(rev.get("comment") or "")).strip()
        comment_html = (
            f'<div class="cmt">«{html.escape(comment)}»</div>'
            if comment
            else f'<div class="cmt" style="color:#9CA3AF;">{s["no_comment"]}</div>'
        )
        code = str(rev.get("order_code") or "—")
        amount = _sf(rev.get("amount"), None)
        amount_str = f"{fmt(amount)}&nbsp;₴" if amount is not None else "—"
        stars = ("★" * rating) + ("☆" * max(0, 5 - rating))
        parts.append(
            f'<div class="rv {tone}">'
            f'<div class="loc">{html.escape(str(rev.get("location") or ""))}</div>'
            f'<div class="stars" style="color:{rc};">{stars} {rating}/5</div>'
            f"{comment_html}"
            f'<div class="meta">'
            f'<div><div class="ml">{s["order_code"]}</div><div class="mv">{html.escape(code)}</div></div>'
            f'<div><div class="ml">{s["order_dt"]}</div><div class="mv">{html.escape(format_order_dt(rev.get("order_dt")))}</div></div>'
            f'<div><div class="ml">{s["order_value"]}</div><div class="mv">{amount_str}</div></div>'
            f"</div></div>"
        )
    return "".join(parts)


def _page(*, title, html_title, period_label, kpis, cards, footer, locale="uk"):
    s = STRINGS.get(locale) or STRINGS["uk"]
    return f"""<!DOCTYPE html>
<html lang="{s['html_lang']}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html.escape(html_title)}</title>
<style>
{CSS}
</style></head><body>
<div class="hero">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
    <div style="background:rgba(52,209,134,.15);border:1px solid rgba(52,209,134,.25);border-radius:6px;padding:4px 9px;font-size:10px;font-weight:700;color:#2AAF6D;">Bolt Food Ukraine</div>
    <span style="margin-left:auto;background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3);border-radius:4px;padding:2px 8px;font-size:9px;font-weight:700;color:#F59E0B;">{s['badge']}</span>
  </div>
  <div class="badge">{html.escape(period_label)}</div>
  <h1>{html.escape(title)}</h1>
  <p class="hero-sub">{html.escape(period_label)}</p>
  <div class="kpis">{kpis}</div>
</div>
<div class="wrap">
<div class="sec">
  <div class="sec-t">{s['reviews']}</div><div class="hr"></div>
  {cards}
</div>
</div>
<div class="footer">Bolt Food Ukraine · {html.escape(footer)} · {html.escape(period_label)} · {s['confidential']}</div>
</body></html>"""


def _kpi_html(reviews, s):
    n = len(reviews)
    commented = sum(1 for r in reviews if str(r.get("comment") or "").strip())
    rated = [int(_sf(r.get("rating"), 0) or 0) for r in reviews if _sf(r.get("rating"))]
    avg = (sum(rated) / len(rated)) if rated else None
    avg_str = f"{avg:.2f} ★" if avg is not None else "—"
    rc = rat_color(avg)
    return (
        f'<div class="kpi"><strong>{n}</strong>{s["ratings"]}</div>'
        f'<div class="kpi"><strong>{commented}</strong>{s["with_comment"]}</div>'
        f'<div class="kpi"><strong style="color:{rc};">{avg_str}</strong>{s["avg"]}</div>'
    )


def build_reviews_report(*, display_name, period_label, period_short, reviews, location_name=None, locale="uk"):
    s = STRINGS.get(locale) or STRINGS["uk"]
    is_network = location_name is None
    title = s["title_network"].format(name=display_name) if is_network else s["title_location"].format(name=location_name)
    html_title = (
        s["html_title_net"].format(name=display_name, period=period_short)
        if is_network
        else s["html_title_loc"].format(name=location_name, period=period_short)
    )
    footer = s["footer_net"] if is_network else s["footer_loc"]
    return _page(
        title=title,
        html_title=html_title,
        period_label=period_label,
        kpis=_kpi_html(reviews, s),
        cards=_review_cards(reviews, s),
        footer=footer,
        locale=locale,
    )

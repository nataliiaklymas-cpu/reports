#!/usr/bin/env python3
"""
Чорноморка — November 2026 marketing budget (3% of October TO).

Same visual/logic as chornomorka_oct2026_marketing_budget.html:
  TO = SUM(order_gmv_local) of delivered orders in the calendar month
  budget = round(TO * 0.03)
  partner promo = campaign_spend_provider_eur * 42

Writes:
  chornomorka/chornomorka_nov2026_marketing_budget.html
  chornomorka/chornomorka_nov2026_budget_data.json
and inserts a link into chornomorka/index.html.

Runnable from nataliiaklymas-cpu/reports (GitHub Actions) or locally
if DATABRICKS_TOKEN / .env is available.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

UAH = 42.0
CUR_START, CUR_END = "2026-10-01", "2026-11-01"
PREV_START, PREV_END = "2026-09-01", "2026-10-01"
OPS_START, OPS_END = "2026-09-28", "2026-11-02"

# Display names from the partner list (Ukrainian), city as on previous budget page.
PROVIDERS = {
    189178: {"name": "Чорноморка Ужгород", "city": "Ужгород"},
    202318: {"name": "Чорноморка на Русанівці", "city": "Київ"},
    202324: {"name": "Чорноморка Преображенська", "city": "Київ"},
    202326: {"name": "Чорноморка Лаврська", "city": "Київ"},
    202333: {"name": "Чорноморка на Петропавлівській Борщагівці", "city": "Київ"},
    202334: {"name": "Чорноморка Ярославська", "city": "Київ"},
    202338: {"name": "Чорноморка Успішна", "city": "Київ"},
    202339: {"name": "Чорноморка Чернівці", "city": "Чернівці"},
    202341: {"name": "Чорноморка Біла Церква", "city": "Біла Церква"},
    202349: {"name": "Чорноморка Велика Васильківська", "city": "Київ"},
    202375: {"name": "Чорноморка Княжий затон", "city": "Київ"},
    202378: {"name": "Чорноморка Івасюка", "city": "Київ"},
    202379: {"name": "Чорноморка Драгоманова", "city": "Київ"},
    202964: {"name": "Чорноморка Вінниця", "city": "Вінниця"},
    203155: {"name": "Чорноморка пр-т Берестейський", "city": "Київ"},
    203170: {"name": "Чорноморка Бровари", "city": "Бровари"},
    203180: {"name": "Чорноморка Черкаси", "city": "Черкаси"},
    203192: {"name": "Чорноморка Буча", "city": "Ірпінь"},
    203194: {"name": "Чорноморка на Печерську", "city": "Київ"},
    203197: {"name": "Чорноморка на Чикаленка", "city": "Київ"},
    832507: {"name": "Чорноморка на Нивках", "city": "Київ"},
    203223: {"name": "Чорноморка в Республіці", "city": "Київ"},
    203228: {"name": "Чорноморка Іллєнка", "city": "Київ"},
    202367: {"name": "Анчоусна від Чорноморки Рівне", "city": "Рівне"},
    203567: {"name": "Анчоусна від Чорноморки Південна", "city": "Дніпро"},
    203578: {"name": "Анчоусна від Чорноморки Барикадна", "city": "Дніпро"},
    202331: {"name": "Чорноморка Луцьк", "city": "Луцьк"},
    5092532: {"name": "Чорноморка Княжий затон (нова)", "city": "Київ"},
    1792503: {"name": "Чорноморка Чернігів", "city": "Чернігів"},
    5842509: {"name": "Чорноморка Житомир", "city": "Житомир"},
    5332630: {"name": "Чорноморка Софіївська Борщагівка (Київська)", "city": "Київ"},
    5392633: {"name": "Чорноморка Ірпінь", "city": "Ірпінь"},
    5392639: {"name": "Чорноморка Софіївська Борщагівка", "city": "Київ"},
}
IDS_STR = ",".join(str(i) for i in PROVIDERS)


def find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for cand in (here, here.parent, Path.cwd()):
        if (cand / "chornomorka").is_dir() and (cand / "automation").is_dir():
            return cand
    # GitHub Actions checkout
    if Path("chornomorka").is_dir():
        return Path(".").resolve()
    return here.parent


def load_dbx():
    root = find_repo_root()
    sys.path.insert(0, str(root / "automation"))
    local = Path("/Users/klymasnataliia/Library/CloudStorage/GoogleDrive-nataliia.klymas@bolt.eu/Мій диск/Cursor/Databricks & QBRs  2")
    if local.exists():
        sys.path.insert(0, str(local))
    from dbx import DBX  # noqa: WPS433
    return DBX()


def sf(v, d=0):
    if v is None:
        return d
    try:
        import math
        if isinstance(v, float) and math.isnan(v):
            return d
    except Exception:
        pass
    return v


def nb(v, d=0):
    return f"{round(float(v or 0), d):,.{d}f}".replace(",", "\u00a0")


def classify(st):
    pos, neg = [], []
    rating = st.get("rating")
    avail = st.get("avail")
    new_u = int(st.get("new_u") or 0)
    bp_sh = int(st.get("bp_sh") or 0)
    r_bad_pct = float(st.get("r_bad_pct") or 0)
    review_cnt = int(st.get("review_cnt") or 0)
    prep = st.get("prep_min") or 0
    if rating and rating >= 4.7:
        pos.append(f"рейтинг {rating:.2f}★")
    if avail and avail >= 0.95:
        pos.append(f"доступність {avail*100:.0f}%")
    if review_cnt > 0 and r_bad_pct == 0 and (not rating or rating >= 4.3):
        pos.append("bad rate 0.0%")
    if bp_sh >= 22:
        pos.append(f"Bolt+ {bp_sh}%")
    if new_u >= 35:
        pos.append(f"{new_u} нових клієнтів")
    if not pos and new_u > 0:
        pos.append(f"{new_u} нових клієнтів")
    pos = pos[:2]
    if avail is not None and avail < 0.90:
        neg.append(f"доступність {avail*100:.0f}% (ціль ≥95%)")
    if rating is not None and rating < 4.3:
        neg.append(f"рейтинг {rating:.2f}★")
    if review_cnt and r_bad_pct >= 10:
        neg.append(f"bad rate {r_bad_pct:.1f}%")
    if prep and prep > 25:
        neg.append(f"час приготування {int(round(prep))} хв")
    return pos, neg


def rat_col(v):
    if not v:
        return "#9CA3AF"
    if v >= 4.7:
        return "#34D186"
    if v >= 4.3:
        return "#F59E0B"
    return "#EF4444"


def av_col(v):
    if not v:
        return "#9CA3AF"
    if v >= 0.95:
        return "#34D186"
    if v >= 0.90:
        return "#F59E0B"
    return "#EF4444"


def row_map(df, pid):
    if df is None or df.empty:
        return {}
    r = df[df["provider_id"] == pid]
    return r.iloc[0].to_dict() if not r.empty else {}


def main():
    root = find_repo_root()
    out_html = root / "chornomorka" / "chornomorka_nov2026_marketing_budget.html"
    out_json = root / "chornomorka" / "chornomorka_nov2026_budget_data.json"
    index_path = root / "chornomorka" / "index.html"
    print(f"repo root: {root}", flush=True)

    dbx = load_dbx()

    def q(sql, label):
        df = dbx.query(sql)
        print(f"  {label}: {len(df)} rows", flush=True)
        return df

    cur = q(f"""
        SELECT provider_id,
            COUNT(*) AS delivered,
            SUM(order_gmv_local) AS gmv_local,
            SUM(order_gmv_eur) AS gmv_eur,
            SUM(COALESCE(campaign_spend_bolt_eur, 0)) AS bolt_promo_eur,
            SUM(COALESCE(campaign_spend_provider_eur, 0)) AS part_promo_eur,
            SUM(CASE WHEN is_bolt_plus_order THEN 1 ELSE 0 END) AS bp_ord
        FROM main.ng_delivery.dim_order_delivery
        WHERE provider_id IN ({IDS_STR}) AND order_state = 'delivered'
          AND order_created_date_local >= DATE('{CUR_START}')
          AND order_created_date_local < DATE('{CUR_END}')
        GROUP BY provider_id
    """, "October orders")

    prev = q(f"""
        SELECT provider_id,
            COUNT(*) AS delivered,
            SUM(order_gmv_local) AS gmv_local
        FROM main.ng_delivery.dim_order_delivery
        WHERE provider_id IN ({IDS_STR}) AND order_state = 'delivered'
          AND order_created_date_local >= DATE('{PREV_START}')
          AND order_created_date_local < DATE('{PREV_END}')
        GROUP BY provider_id
    """, "September orders")

    new_u = q(f"""
        SELECT provider_id, COUNT(*) AS new_u FROM (
            SELECT provider_id, user_id, MIN(order_created_date_local) AS first_order
            FROM main.ng_delivery.dim_order_delivery
            WHERE provider_id IN ({IDS_STR}) AND order_state = 'delivered'
            GROUP BY provider_id, user_id
        )
        WHERE first_order >= DATE('{CUR_START}') AND first_order < DATE('{CUR_END}')
        GROUP BY provider_id
    """, "October new customers")

    first_seen = q(f"""
        SELECT provider_id, MIN(order_created_date_local) AS first_dt
        FROM main.ng_delivery.dim_order_delivery
        WHERE provider_id IN ({IDS_STR}) AND order_state = 'delivered'
        GROUP BY provider_id
    """, "first delivered")

    rat = q(f"""
        SELECT provider_id,
            ROUND(AVG(rating_value), 2) AS rating,
            COUNT(*) AS review_cnt,
            SUM(CASE WHEN rating_value <= 2 THEN 1 ELSE 0 END) AS bad_cnt
        FROM main.ng_delivery.delivery_rating_provider_rating_history
        WHERE provider_id IN ({IDS_STR})
          AND created_date >= DATE('{CUR_START}') AND created_date < DATE('{CUR_END}')
        GROUP BY provider_id
    """, "October ratings")

    ops = q(f"""
        SELECT provider_id,
            SUM(provider_active_rate_value * provider_active_rate_weight)
                / NULLIF(SUM(provider_active_rate_weight), 0) AS avail,
            SUM(provider_processing_minutes_per_order_value * provider_processing_minutes_per_order_weight)
                / NULLIF(SUM(provider_processing_minutes_per_order_weight), 0) AS prep_min
        FROM main.ng_delivery.fact_provider_weekly
        WHERE provider_id IN ({IDS_STR})
          AND metric_timestamp_partition >= DATE('{OPS_START}')
          AND metric_timestamp_partition < DATE('{OPS_END}')
        GROUP BY provider_id
    """, "October ops")

    dbx.close()

    rows = []
    for pid, meta in PROVIDERS.items():
        c = row_map(cur, pid)
        p = row_map(prev, pid)
        r = row_map(rat, pid)
        o = row_map(ops, pid)
        n = row_map(new_u, pid)
        fs = row_map(first_seen, pid)
        delivered = int(sf(c.get("delivered", 0)))
        gmv = int(round(float(sf(c.get("gmv_local", 0)))))
        budget = int(round(gmv * 0.03))
        prev_del = int(sf(p.get("delivered", 0)))
        prev_gmv = int(round(float(sf(p.get("gmv_local", 0)))))
        part_promo = int(round(float(sf(c.get("part_promo_eur", 0))) * UAH))
        bolt_promo = int(round(float(sf(c.get("bolt_promo_eur", 0))) * UAH))
        bp_ord = int(sf(c.get("bp_ord", 0)))
        bp_sh = round(bp_ord / max(delivered, 1) * 100)
        rating = sf(r.get("rating"), None)
        review_cnt = int(sf(r.get("review_cnt", 0)))
        bad_cnt = int(sf(r.get("bad_cnt", 0)))
        r_bad_pct = round(bad_cnt / max(review_cnt, 1) * 100, 1) if review_cnt else 0.0
        avail = sf(o.get("avail"), None)
        prep = sf(o.get("prep_min"), 0)
        new_users = int(sf(n.get("new_u", 0)))
        first_dt = str(fs.get("first_dt") or "")[:10]
        is_new = bool(first_dt and first_dt >= "2026-10-01")
        st = dict(
            rating=rating, avail=avail, new_u=new_users, bp_sh=bp_sh,
            r_bad_pct=r_bad_pct, review_cnt=review_cnt, prep_min=prep,
        )
        pos, neg = classify(st)
        if is_new and delivered:
            pos = [f"старт у жовтні"] + pos
            pos = pos[:2]
        if delivered == 0:
            if not neg:
                neg = ["немає доставлених замовлень у жовтні"]
        mom_ord = round((delivered - prev_del) / prev_del * 100, 1) if prev_del else None
        mom_gmv = round((gmv - prev_gmv) / prev_gmv * 100, 1) if prev_gmv else None
        rows.append(dict(
            pid=pid, name=meta["name"], city=meta["city"],
            gmv=gmv, budget=budget, orders=delivered,
            prev_gmv=prev_gmv, prev_orders=prev_del,
            mom_ord=mom_ord, mom_gmv=mom_gmv,
            rating=rating, avail=avail, new_u=new_users,
            part_promo=part_promo, bolt_promo=bolt_promo,
            bp_ord=bp_ord, bp_sh=bp_sh, review_cnt=review_cnt,
            r_bad_pct=r_bad_pct, first_dt=first_dt, is_new=is_new,
            pos=pos, neg=neg,
        ))

    rows.sort(key=lambda x: -x["gmv"])
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    total_gmv = sum(x["gmv"] for x in rows)
    total_budget = sum(x["budget"] for x in rows)
    total_orders = sum(x["orders"] for x in rows)
    total_new = sum(x["new_u"] for x in rows)
    total_part = sum(x["part_promo"] for x in rows)
    total_bolt = sum(x["bolt_promo"] for x in rows)
    total_prev_gmv = sum(x["prev_gmv"] for x in rows)
    total_prev_orders = sum(x["prev_orders"] for x in rows)
    rated = [x["rating"] for x in rows if x["rating"]]
    avg_rating = round(sum(rated) / len(rated), 2) if rated else None
    active = sum(1 for x in rows if x["orders"] > 0)
    mom_ord = round((total_orders - total_prev_orders) / total_prev_orders * 100, 1) if total_prev_orders else None
    mom_gmv = round((total_gmv - total_prev_gmv) / total_prev_gmv * 100, 1) if total_prev_gmv else None

    loc_rows_html = ""
    for r in rows:
        pos_html = " · ".join(r["pos"][:2]) if r["pos"] else '<span style="color:#9CA3AF;">—</span>'
        neg_html = " · ".join(r["neg"]) if r["neg"] else '<span style="color:#9CA3AF;">без критичних зон</span>'
        rat_str = f"{r['rating']:.2f}★" if r["rating"] else "—"
        av_str = f"{r['avail']*100:.0f}%" if r["avail"] else "—"
        loc_rows_html += f"""<tr>
      <td><strong>{r['name']}</strong><div style="font-size:10px;color:#9CA3AF;">ID {r['pid']} · {r['city']}</div></td>
      <td class="num">{nb(r['gmv'])}&nbsp;₴</td>
      <td class="num"><strong style="color:#F59E0B;">{nb(r['budget'])}&nbsp;₴</strong></td>
      <td class="num">{r['orders']}</td>
      <td class="num"><span style="color:{rat_col(r['rating'])};font-weight:700;">{rat_str}</span></td>
      <td class="num"><span style="color:{av_col(r['avail'])};font-weight:700;">{av_str}</span></td>
      <td class="num">{nb(r['part_promo'])}&nbsp;₴</td>
      <td style="font-size:11px;color:#065F46;">{pos_html}</td>
      <td style="font-size:11px;color:#92400E;">{neg_html}</td>
    </tr>"""

    zero_names = [x["name"] for x in rows if x["orders"] == 0]
    zero_note = ""
    if zero_names:
        zero_note = (
            " " + ", ".join(zero_names)
            + " у жовтні не мали доставлених замовлень — бюджет на листопад по них 0&nbsp;₴, "
            "поки точка не відновить роботу."
        )

    def mom_txt(pct):
        if pct is None:
            return "—"
        sign = "+" if pct > 0 else ""
        return f"{sign}{pct:.1f}%"

    mom_note = (
        f"Порівняння з вереснем по цьому списку точок: замовлення {nb(total_prev_orders)} → "
        f"{nb(total_orders)} ({mom_txt(mom_ord)}), ТО {nb(total_prev_gmv)} → {nb(total_gmv)}&nbsp;₴ "
        f"({mom_txt(mom_gmv)})."
    )

    html = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Чорноморка — маркетинговий бюджет на листопад 2026 (на основі жовтня)</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#F8F9FA;color:#1A1A1A;line-height:1.6;max-width:1280px;margin:0 auto;padding:0 0 40px;}}
.hero{{color:white;padding:32px 32px 26px;background:linear-gradient(135deg,#0a1628 0%,#0d2a4a 60%,#0f3460 100%);}}
.badge{{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;padding:4px 12px;border-radius:4px;margin-bottom:12px;background:#1565C0;}}
.hero h1{{font-size:24px;font-weight:800;margin-bottom:6px;}}
.hero-sub{{font-size:13px;color:rgba(255,255,255,.55);margin-bottom:18px;}}
.kpis{{display:flex;gap:22px;flex-wrap:wrap;}}
.kpi{{font-size:12px;color:rgba(255,255,255,.45);}}
.kpi strong{{display:block;font-size:22px;font-weight:700;color:white;margin-bottom:1px;}}
.wrap{{padding:26px 28px;}}
.sec-t{{font-size:16px;font-weight:700;margin-bottom:4px;}}
.sec-s{{font-size:12px;color:#6B7280;margin-bottom:14px;}}
.hr{{height:1px;background:#E8E8E8;margin:0 0 16px;}}
table{{width:100%;border-collapse:collapse;font-size:12px;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05);}}
th{{background:#F5F8FF;padding:9px 10px;text-align:left;font-size:10px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid #E8E8E8;}}
td{{padding:9px 10px;border-bottom:1px solid #F3F4F6;vertical-align:middle;}}
.num{{text-align:right;font-variant-numeric:tabular-nums;}}
tr.total td{{background:#F5F8FF;font-weight:800;border-top:2px solid #1565C0;}}
.note{{font-size:11px;color:#9CA3AF;margin-top:14px;}}
.card{{background:white;border-radius:12px;padding:16px 18px;margin-bottom:14px;box-shadow:0 2px 10px rgba(0,0,0,.05);}}
.footer{{background:#0d2a1a;color:rgba(255,255,255,.3);text-align:center;padding:16px;font-size:11px;margin-top:28px;}}
</style></head><body>

<div class="hero">
  <div class="badge">ЛИСТОПАД 2026 · МАРКЕТИНГОВИЙ БЮДЖЕТ</div>
  <h1>Чорноморка — розрахунок маркетингового бюджету на листопад</h1>
  <p class="hero-sub">3% від товарообігу за жовтень 2026 · {len(rows)} локацій ({active} з замовленнями). Якщо заклад не погоджує активність — Bolt Food активує промо або рекламу на цю суму самостійно.</p>
  <div class="kpis">
    <div class="kpi"><strong>{nb(total_gmv)}&nbsp;₴</strong>ТО мережі, жовтень</div>
    <div class="kpi"><strong style="color:#FCD34D;">{nb(total_budget)}&nbsp;₴</strong>Бюджет на листопад (3%)</div>
    <div class="kpi"><strong>{nb(total_orders)}</strong>Доставлено, жовтень</div>
    <div class="kpi"><strong>{avg_rating:.2f}&nbsp;★</strong>Сер. рейтинг мережі</div>
    <div class="kpi"><strong style="color:#C4B5FD;">{nb(total_new)}</strong>Нових клієнтів</div>
  </div>
</div>

<div class="wrap">
  <div class="card" style="border-left:4px solid #1565C0;margin-bottom:22px;">
    <div style="font-size:10px;font-weight:700;color:#1565C0;letter-spacing:.6px;text-transform:uppercase;margin-bottom:6px;">Як працюватиме інвестиція</div>
    <div style="font-size:14px;font-weight:700;margin-bottom:8px;">Обовʼязкові 3% від ТО — промо або реклама на розсуд Bolt Food, якщо немає погодження від закладу</div>
    <div style="font-size:12px;color:#4B5563;line-height:1.6;">
      Відповідно до угоди кожна локація щомісяця інвестує в маркетинг до 3% від свого ТО на платформі.
      Якщо заклад не підтверджує конкретну активність, Bolt Food активує промо та/або платне просування на суму бюджету цієї точки.
      Заклад отримує замовлення <strong>по повній вартості меню</strong> — знижки пробивати на касі / в POS не потрібно: компенсація проходить через платформу.
      У жовтні активності вже запускались у межах цієї умови: партнер промо {nb(total_part)}&nbsp;₴, Bolt промо {nb(total_bolt)}&nbsp;₴.{zero_note}
    </div>
  </div>

  <div class="sec-t">Розбивка по локаціях</div>
  <div class="sec-s">ТО — до знижок, доставлені замовлення · Бюджет листопада = 3% від ТО жовтня · «Партнер промо, жовтень» — фактичні витрати партнера на знижки за жовтень (курс 42&nbsp;₴/€)</div>
  <div class="hr"></div>
  <div style="overflow-x:auto;">
  <table><thead><tr>
    <th>Локація</th><th class="num">ТО жовтень</th><th class="num">Бюджет листопад (3%)</th>
    <th class="num">Доставлено</th><th class="num">Рейтинг</th><th class="num">Доступність</th>
    <th class="num">Партнер промо, жовт.</th>
    <th>Сильні сторони</th><th>Зони росту</th>
  </tr></thead><tbody>
    {loc_rows_html}
    <tr class="total"><td>Разом, {len(rows)} локацій</td><td class="num">{nb(total_gmv)}&nbsp;₴</td>
      <td class="num" style="color:#B45309;">{nb(total_budget)}&nbsp;₴</td>
      <td class="num">{nb(total_orders)}</td><td class="num">{avg_rating:.2f}&nbsp;★</td><td class="num">—</td>
      <td class="num">{nb(total_part)}&nbsp;₴</td><td></td><td></td></tr>
  </tbody></table>
  </div>
  <div class="note">Дані Databricks · жовтень 2026 (1–31.10) · ТО = order_gmv_local (до знижок), як у розрахунках за липень, серпень і вересень. Партнер промо у таблиці — campaign_spend_provider_eur × 42 (як у тижневих звітах). {mom_note}</div>
</div>

<div class="footer">Bolt Food Ukraine × Чорноморка · Маркетинговий бюджет · Листопад 2026 · Конфіденційно</div>
</body></html>"""
    out_html.write_text(html, encoding="utf-8")

    if index_path.exists():
        idx = index_path.read_text(encoding="utf-8")
        li = ('<li><a href="chornomorka_nov2026_marketing_budget.html">'
              '<span class="t">Маркетинговий бюджет на листопад 2026 (розрахунок за жовтень)</span>'
              '<span class="arw">\u2192</span></a></li>')
        if "chornomorka_nov2026_marketing_budget.html" not in idx:
            idx = idx.replace('<ul class="list">', '<ul class="list">\n      ' + li, 1)
            index_path.write_text(idx, encoding="utf-8")
            print("index.html updated", flush=True)

    facts = dict(
        total_gmv=total_gmv, total_budget=total_budget, total_orders=total_orders,
        total_new=total_new, avg_rating=avg_rating, active=active, n=len(rows),
        total_part=total_part, total_bolt=total_bolt,
        total_prev_gmv=total_prev_gmv, total_prev_orders=total_prev_orders,
        mom_ord=mom_ord, mom_gmv=mom_gmv,
        top_orders=sorted(rows, key=lambda x: -x["orders"])[:6],
        top_new=sorted(rows, key=lambda x: -x["new_u"])[:6],
        top_rating=[x for x in sorted(rows, key=lambda x: (-(x["rating"] or 0), -x["orders"])) if x["rating"] and x["rating"] >= 4.9][:8],
        grown=[x for x in rows if (x["mom_ord"] or 0) >= 15],
        low_avail=[x for x in rows if x["avail"] is not None and x["avail"] < 0.90],
        low_rating=[x for x in rows if x["rating"] is not None and x["rating"] < 4.3],
        dropped=[x for x in sorted(rows, key=lambda x: (x["mom_ord"] if x["mom_ord"] is not None else 0)) if x["prev_orders"] >= 15 and (x["mom_ord"] or 0) <= -30][:6],
        zero=zero_names,
        new_locs=[x for x in rows if x["is_new"]],
    )
    facts_path = root / "chornomorka" / "chornomorka_nov2026_letter_facts.json"

    def slim(x):
        return dict(pid=x["pid"], name=x["name"], orders=x["orders"], gmv=x["gmv"],
                    budget=x["budget"], rating=x["rating"], new_u=x["new_u"],
                    mom_ord=x["mom_ord"], mom_gmv=x["mom_gmv"], avail=x["avail"],
                    part_promo=x["part_promo"], bolt_promo=x["bolt_promo"])

    facts["top_orders"] = [slim(x) for x in facts["top_orders"]]
    facts["top_new"] = [slim(x) for x in facts["top_new"]]
    facts["top_rating"] = [slim(x) for x in facts["top_rating"]]
    facts["grown"] = [slim(x) for x in facts["grown"]]
    facts["low_avail"] = [slim(x) for x in facts["low_avail"]]
    facts["low_rating"] = [slim(x) for x in facts["low_rating"]]
    facts["dropped"] = [slim(x) for x in facts["dropped"]]
    facts["new_locs"] = [slim(x) for x in facts["new_locs"]]
    facts_path.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"HTML: {out_html}", flush=True)
    print(f"JSON: {out_json}", flush=True)
    print(f"FACTS: {facts_path}", flush=True)
    print(f"TO {total_gmv}  budget {total_budget}  orders {total_orders}  new {total_new}  rating {avg_rating}", flush=True)
    print(f"MoM orders {total_prev_orders}->{total_orders} ({mom_ord})  GMV {total_prev_gmv}->{total_gmv} ({mom_gmv})", flush=True)
    print(f"promo partner {total_part} bolt {total_bolt}", flush=True)


if __name__ == "__main__":
    main()

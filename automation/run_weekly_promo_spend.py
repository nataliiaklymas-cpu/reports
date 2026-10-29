#!/usr/bin/env python3
from __future__ import annotations
"""
Weekly Muza / Europiano promo-spend report.

Writes:
  {repo_root}/muza/weekly-promo-spend/muza_promo_spend_YYYYMMDD_YYYYMMDD.html
  {repo_root}/muza/weekly-promo-spend/muza_promo_spend_YYYYMMDD_YYYYMMDD.xlsx
  {repo_root}/muza/weekly-promo-spend/index.html

Default window is the previous full Mon–Sun week. Use --backfill-from to
generate every missing week up to that target.
"""

import argparse
import base64
import datetime as dt
import math
import os
import re
from pathlib import Path

import pandas as pd

from dbx import DBX
from partners_config import EUROPIANO_PROVIDERS, MUZA_PROVIDERS

UAH = 42.0
FOLDER = "muza/weekly-promo-spend"
CITY_EN = {
    "Київ": "Kyiv",
    "Львів": "Lviv",
    "Рівне": "Rivne",
    "Ірпінь": "Irpin",
    "Дніпро": "Dnipro",
    "Черкаси": "Cherkasy",
}


def promo_providers():
    out = {}
    for src in (MUZA_PROVIDERS, EUROPIANO_PROVIDERS):
        for pid, meta in src.items():
            name = meta["name"]
            for prefix in ("Муза ", "Європіано "):
                if name.startswith(prefix):
                    name = name[len(prefix):]
                    break
            out[int(pid)] = {
                "name": name,
                "city": CITY_EN.get(meta["city"], meta["city"]),
                "brand": meta["brand"],
            }
    return out


def prev_full_week(today: dt.date) -> tuple[dt.date, dt.date]:
    this_mon = today - dt.timedelta(days=today.weekday())
    prev_mon = this_mon - dt.timedelta(days=7)
    return prev_mon, prev_mon + dt.timedelta(days=6)


def weeks_in_range(start: dt.date, end: dt.date) -> list[tuple[dt.date, dt.date]]:
    mon = start - dt.timedelta(days=start.weekday())
    last_mon = end - dt.timedelta(days=end.weekday())
    weeks = []
    while mon <= last_mon:
        weeks.append((mon, mon + dt.timedelta(days=6)))
        mon += dt.timedelta(days=7)
    return weeks


def safe(v, d=0):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return d
    return v


def fmt(n, dec=0):
    n = safe(n, 0)
    if dec:
        return f"{round(float(n), dec):,.{dec}f}".replace(",", "\u00a0")
    return f"{int(round(float(n))):,}".replace(",", "\u00a0")


def money(n):
    return f"{fmt(n)}\u00a0₴"


def load_assets(repo_root: Path):
    font = repo_root / "internal" / "fonts" / "Inter-VariableFont.ttf"
    logo = repo_root / "automation" / "assets" / "Bolt-Food_logo-stacked_White_RGB.png"
    inter_b64 = base64.b64encode(font.read_bytes()).decode("ascii")
    logo_uri = f"data:image/png;base64,{base64.b64encode(logo.read_bytes()).decode('ascii')}"
    style = f"""<style>
@font-face{{font-family:"InterVariable";src:url("data:font/ttf;base64,{inter_b64}") format("truetype-variations");font-weight:100 900;font-style:normal;font-display:swap;}}
:root{{--ac:#2A9C64;--acd:#0C2C1C;--lt:#8FD3AC;--dark:#191F1C;--gray:#EEF1F0;--surface:#F3F5F4;--border:#DEE2E1;--muted:#5F6563;--font:"InterVariable",Inter,system-ui,sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{background:var(--gray);color:var(--dark);}}
body{{font-family:var(--font);font-feature-settings:"cv03","cv04","liga" 1,"calt" 1;-webkit-font-smoothing:antialiased;line-height:1.55;letter-spacing:-.011em;}}
.num,table,td.num,th.num,.kpi strong{{font-feature-settings:"tnum","cv03","cv04";}}
.hero{{background:var(--acd);color:#fff;padding:40px 48px;border-left:4px solid var(--ac);}}
.hero-top{{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px;flex-wrap:wrap;}}
.hero-kicker{{font-size:11px;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.55);}}
.hero-logo{{height:40px;display:block;}}
.hbadge{{display:inline-block;background:var(--ac);color:#fff;font-size:11px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;padding:5px 12px;border-radius:600rem;margin-bottom:14px;}}
.hero h1{{font-size:27px;font-weight:650;line-height:1.2;margin-bottom:8px;letter-spacing:-.02em;}}
.hero h1 span{{color:#8FD3AC;}}
.hero-sub{{font-size:13px;color:rgba(255,255,255,.6);margin-bottom:22px;}}
.kpis{{display:flex;gap:26px;flex-wrap:wrap;}}
.kpi{{font-size:12px;color:rgba(255,255,255,.5);}}
.kpi strong{{display:block;font-size:20px;font-weight:650;color:#fff;margin-bottom:1px;}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 26px;}}
.sec{{padding:34px 0;}}
.sec-t{{font-size:19px;font-weight:650;margin-bottom:5px;letter-spacing:-.02em;}}
.sec-s{{font-size:13px;color:var(--muted);margin-bottom:18px;}}
.hr{{height:1px;background:var(--border);margin:0 0 20px;}}
.card{{background:#fff;border-radius:16px;padding:16px;}}
.g4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}}
@media(max-width:900px){{.g4{{grid-template-columns:1fr 1fr;}}}}
.cl{{font-size:11px;font-weight:650;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;}}
.cv{{font-size:22px;font-weight:650;margin-bottom:2px;letter-spacing:-.02em;}}
.cd{{font-size:12px;color:var(--muted);}}
table{{width:100%;border-collapse:collapse;font-size:13px;}}
th{{background:var(--surface);padding:9px 10px;text-align:left;font-size:10px;font-weight:650;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border);position:sticky;top:0;}}
td{{padding:9px 10px;border-bottom:1px solid var(--border);vertical-align:middle;}}
tr:hover td{{background:var(--surface);}}
.num{{text-align:right;}}
.b{{display:inline-block;padding:3px 10px;border-radius:600rem;font-size:11px;font-weight:650;}}
.bg{{background:rgba(42,156,100,.14);color:#187B51;}}
.brand-h{{font-size:14px;font-weight:650;margin:26px 0 10px;}}
.tot td{{font-weight:650;background:var(--surface);}}
.scroll{{overflow:auto;max-height:640px;border-radius:16px;background:#fff;}}
.foot{{padding:28px 0 48px;font-size:12px;color:var(--muted);}}
.nav{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;}}
.nav a{{font-size:12px;font-weight:650;color:var(--ac);text-decoration:none;background:#fff;border-radius:600rem;padding:6px 12px;}}
</style>"""
    return style, logo_uri


def render_week(providers, loc_week, orders_week, start, end, style, logo_uri, out_dir: Path):
    ids = list(providers.keys())
    week_label = f"{start.day}.{start.month:02d}–{end.day}.{end.month:02d}.{end.year}"
    file_stub = f"muza_promo_spend_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}"

    L = {}
    for pid in ids:
        meta = providers[pid]
        r = loc_week.loc[pid] if pid in loc_week.index else None
        if r is not None:
            delivered = int(safe(r["delivered"]))
            gmv = round(safe(r["gmv_eur"]) * UAH)
            bolt = round(safe(r["bolt_promo_eur"]) * UAH)
            part = round(safe(r["part_promo_eur"]) * UAH)
            promo_ord = int(safe(r["promo_ord"]))
        else:
            delivered = gmv = bolt = part = promo_ord = 0
        L[pid] = {
            **meta,
            "delivered": delivered,
            "gmv": gmv,
            "bolt": bolt,
            "part": part,
            "total": bolt + part,
            "promo_ord": promo_ord,
            "promo_sh": round(promo_ord / max(delivered, 1) * 100) if delivered else 0,
        }

    orders = orders_week.copy() if orders_week is not None and not orders_week.empty else pd.DataFrame()
    if not orders.empty:
        orders["bolt_uah"] = (orders["bolt_promo_eur"].astype(float) * UAH).round(0).astype(int)
        orders["part_uah"] = (orders["part_promo_eur"].astype(float) * UAH).round(0).astype(int)
        orders["gmv_uah"] = orders["order_gmv_uah"].astype(float).round(0).astype(int)
        orders["total_uah"] = orders["bolt_uah"] + orders["part_uah"]
        orders["brand"] = orders["provider_id"].map(lambda x: providers.get(int(x), {}).get("brand", ""))
        orders["loc"] = orders["provider_id"].map(lambda x: providers.get(int(x), {}).get("name", ""))
        orders["city"] = orders["provider_id"].map(lambda x: providers.get(int(x), {}).get("city", ""))

    net_del = sum(d["delivered"] for d in L.values())
    net_gmv = sum(d["gmv"] for d in L.values())
    net_bolt = sum(d["bolt"] for d in L.values())
    net_part = sum(d["part"] for d in L.values())
    net_total = net_bolt + net_part
    net_promo_ord = sum(d["promo_ord"] for d in L.values())
    bolt_sh = round(net_bolt / max(net_total, 1) * 100)
    part_sh = round(net_part / max(net_total, 1) * 100)

    def loc_rows(brand: str) -> str:
        rows = []
        pids = sorted(
            [p for p in ids if L[p]["brand"] == brand],
            key=lambda p: (-L[p]["total"], L[p]["city"], L[p]["name"]),
        )
        tb = tp = tt = td = tg = tpo = 0
        for pid in pids:
            d = L[pid]
            tb += d["bolt"]; tp += d["part"]; tt += d["total"]
            td += d["delivered"]; tg += d["gmv"]; tpo += d["promo_ord"]
            rows.append(
                f"<tr><td>{d['name']}</td><td>{d['city']}</td>"
                f"<td class='num'>{fmt(d['delivered'])}</td>"
                f"<td class='num'>{money(d['gmv'])}</td>"
                f"<td class='num' style='color:var(--ac);'>{money(d['bolt'])}</td>"
                f"<td class='num'>{money(d['part'])}</td>"
                f"<td class='num'><strong>{money(d['total'])}</strong></td>"
                f"<td class='num'>{fmt(d['promo_ord'])}</td>"
                f"<td class='num'><span class='b bg'>{d['promo_sh']}%</span></td></tr>"
            )
        rows.append(
            f"<tr class='tot'><td colspan='2'>Разом {brand}</td>"
            f"<td class='num'>{fmt(td)}</td><td class='num'>{money(tg)}</td>"
            f"<td class='num'>{money(tb)}</td><td class='num'>{money(tp)}</td>"
            f"<td class='num'>{money(tt)}</td><td class='num'>{fmt(tpo)}</td><td></td></tr>"
        )
        return "\n".join(rows)

    parts = [f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Муза × Bolt Food — Промо-витрати {week_label}</title>
{style}</head><body>"""]
    parts.append(f"""
<div class="hero"><div class="wrap">
 <div class="hero-top">
   <span class="hero-kicker">Партнерська аналітика · Bolt Food Ukraine × Муза / Європіано</span>
   <img class="hero-logo" src="{logo_uri}" alt="Bolt Food">
 </div>
 <div class="hbadge">Щотижневий звіт · {week_label}</div>
 <h1>Витрати на промо <span>Bolt vs заклад</span></h1>
 <p class="hero-sub">{len(ids)} локацій · доставлені замовлення · дані Databricks</p>
 <div class="kpis">
   <div class="kpi"><strong>{fmt(net_del)}</strong>доставлено</div>
   <div class="kpi"><strong>{money(net_gmv)}</strong>GMV</div>
   <div class="kpi"><strong>{money(net_bolt)}</strong>витрати Bolt ({bolt_sh}%)</div>
   <div class="kpi"><strong>{money(net_part)}</strong>витрати закладу ({part_sh}%)</div>
   <div class="kpi"><strong>{money(net_total)}</strong>промо разом</div>
   <div class="kpi"><strong>{fmt(net_promo_ord)}</strong>замовлень з промо</div>
 </div>
</div></div>
<div class="sec" style="background:#fff;"><div class="wrap">
 <div class="nav"><a href="#by-loc">По локаціях</a><a href="#by-order">По замовленнях</a></div>
</div></div>
<div class="sec" style="background:var(--surface);"><div class="wrap">
 <div class="sec-t">Підсумок тижня</div>
 <div class="sec-s">Розподіл фінансування промо між Bolt і закладом</div><div class="hr"></div>
 <div class="g4">
  <div class="card"><div class="cl">Витрати Bolt</div><div class="cv" style="color:var(--ac);">{money(net_bolt)}</div><div class="cd">{bolt_sh}% від промо</div></div>
  <div class="card"><div class="cl">Витрати закладу</div><div class="cv">{money(net_part)}</div><div class="cd">{part_sh}% від промо</div></div>
  <div class="card"><div class="cl">Разом промо</div><div class="cv">{money(net_total)}</div><div class="cd">{fmt(net_promo_ord)} замовлень</div></div>
  <div class="card"><div class="cl">GMV тижня</div><div class="cv">{money(net_gmv)}</div><div class="cd">{fmt(net_del)} доставок</div></div>
 </div>
</div></div>
<div class="sec" id="by-loc" style="background:#fff;"><div class="wrap">
 <div class="sec-t">Розріз по локаціях</div>
 <div class="sec-s">Доставлено / GMV / витрати Bolt і закладу / частка замовлень з промо</div><div class="hr"></div>
""")
    for brand in ["Муза", "Європіано"]:
        parts.append(f"""
 <div class="brand-h">{brand}</div>
 <div class="card" style="padding:0;overflow:auto;">
 <table>
  <thead><tr>
   <th>Локація</th><th>Місто</th><th class="num">Доставлено</th><th class="num">GMV</th>
   <th class="num">Bolt</th><th class="num">Заклад</th><th class="num">Разом</th>
   <th class="num">З промо</th><th class="num">Частка</th>
  </tr></thead>
  <tbody>{loc_rows(brand)}</tbody>
 </table></div>""")
    parts.append("</div></div>")
    parts.append(f"""
<div class="sec" id="by-order" style="background:var(--surface);"><div class="wrap">
 <div class="sec-t">Розріз по замовленнях</div>
 <div class="sec-s">Лише замовлення з промо-витратами · код / дата / вартість / Bolt / партнер · {fmt(len(orders))} рядків</div><div class="hr"></div>
 <div class="scroll"><table>
  <thead><tr>
   <th>Дата</th><th>Код замовлення</th><th>Бренд</th><th>Локація</th><th>Місто</th>
   <th class="num">Вартість</th><th class="num">Bolt</th><th class="num">Заклад</th><th class="num">Разом</th>
  </tr></thead><tbody>
""")
    if orders.empty:
        parts.append("<tr><td colspan='9'>За цей тиждень промо-замовлень немає.</td></tr>")
    else:
        for _, r in orders.iterrows():
            od = pd.Timestamp(r["order_date"]).strftime("%Y-%m-%d")
            parts.append(
                f"<tr><td>{od}</td><td>{r['order_code']}</td><td>{r['brand']}</td>"
                f"<td>{r['loc']}</td><td>{r['city']}</td>"
                f"<td class='num'>{money(r['gmv_uah'])}</td>"
                f"<td class='num' style='color:var(--ac);'>{money(r['bolt_uah'])}</td>"
                f"<td class='num'>{money(r['part_uah'])}</td>"
                f"<td class='num'><strong>{money(r['total_uah'])}</strong></td></tr>"
            )
    parts.append("</tbody></table></div></div></div>")
    parts.append(f"""
<div class="foot"><div class="wrap">
 Джерело: main.ng_delivery.dim_order_delivery · курс {UAH} ₴/€ · згенеровано {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} · тиждень {start.isoformat()} — {end.isoformat()}
</div></div>
</body></html>""")

    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{file_stub}.html"
    html_path.write_text("".join(parts), encoding="utf-8")

    loc_df = pd.DataFrame([
        {
            "Provider ID": pid,
            "Бренд": L[pid]["brand"],
            "Локація": L[pid]["name"],
            "Місто": L[pid]["city"],
            "Доставлено": L[pid]["delivered"],
            "GMV, ₴": L[pid]["gmv"],
            "Витрати Bolt, ₴": L[pid]["bolt"],
            "Витрати закладу, ₴": L[pid]["part"],
            "Разом промо, ₴": L[pid]["total"],
            "Замовлень з промо": L[pid]["promo_ord"],
            "Частка з промо, %": L[pid]["promo_sh"],
        }
        for pid in ids
    ])
    if orders.empty:
        ord_df = pd.DataFrame(columns=[
            "Дата", "Код замовлення", "order_id", "Бренд", "Локація", "Місто",
            "Вартість замовлення, ₴", "Витрати Bolt, ₴", "Витрати закладу, ₴", "Разом промо, ₴",
        ])
    else:
        ord_df = pd.DataFrame({
            "Дата": pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m-%d"),
            "Код замовлення": orders["order_code"],
            "order_id": orders["order_id"],
            "Бренд": orders["brand"],
            "Локація": orders["loc"],
            "Місто": orders["city"],
            "Вартість замовлення, ₴": orders["gmv_uah"],
            "Витрати Bolt, ₴": orders["bolt_uah"],
            "Витрати закладу, ₴": orders["part_uah"],
            "Разом промо, ₴": orders["total_uah"],
        })
    xlsx_path = out_dir / f"{file_stub}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        loc_df.to_excel(w, sheet_name="По локаціях", index=False)
        ord_df.to_excel(w, sheet_name="По замовленнях", index=False)
        pd.DataFrame([{
            "Тиждень з": start.isoformat(),
            "Тиждень по": end.isoformat(),
            "Доставлено": net_del,
            "GMV, ₴": net_gmv,
            "Bolt, ₴": net_bolt,
            "Заклад, ₴": net_part,
            "Разом промо, ₴": net_total,
            "Замовлень з промо": net_promo_ord,
        }]).to_excel(w, sheet_name="Підсумок", index=False)

    print(f"  {file_stub}: bolt={net_bolt} part={net_part} promo_ord={len(orders)}")
    return html_path.name, f"Промо-витрати {start.day:02d}.{start.month:02d}–{end.day:02d}.{end.month:02d}.{end.year}"


def rebuild_index(out_dir: Path):
    items = []
    for html in sorted(out_dir.glob("muza_promo_spend_*.html"), reverse=True):
        m = re.search(r"muza_promo_spend_(\d{8})_(\d{8})", html.name)
        if not m:
            continue
        start = dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        end = dt.datetime.strptime(m.group(2), "%Y%m%d").date()
        label = f"Промо-витрати {start.day:02d}.{start.month:02d}–{end.day:02d}.{end.month:02d}.{end.year}"
        items.append(
            f'      <li><a href="{html.name}"><span class="t">{label}</span>'
            f'<span class="arw">→</span></a></li>'
        )
    lis = "\n".join(items)
    (out_dir / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Муза — щотижневі витрати на промо</title>
<style>
  :root {{ --green:#34D186; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #fff; min-height: 100vh; padding: 56px 24px;
    background: radial-gradient(1000px 700px at 15% 5%, #1b6b47 0%, transparent 58%), radial-gradient(900px 650px at 95% 95%, #0e3d2a 0%, transparent 55%), linear-gradient(135deg, #0c1f16 0%, #0a1712 100%); }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  .badge {{ display:inline-flex; align-items:center; gap:8px; background:rgba(52,209,134,0.15); color:var(--green); border:1px solid rgba(52,209,134,0.35); padding:6px 13px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.3px; margin-bottom:18px; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:var(--green); }}
  h1 {{ font-size:30px; font-weight:800; letter-spacing:-.5px; margin-bottom:6px; }}
  .sub {{ color:rgba(255,255,255,0.6); font-size:15px; margin-bottom:30px; }}
  .list {{ list-style:none; display:flex; flex-direction:column; gap:12px; }}
  .list a {{ display:flex; align-items:center; justify-content:space-between; gap:16px; text-decoration:none; color:#fff;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:18px 20px; }}
  .list a:hover {{ background:rgba(52,209,134,0.12); border-color:rgba(52,209,134,0.4); }}
  .list .t {{ font-weight:600; font-size:16px; }}
  .list .arw {{ color:var(--green); font-size:18px; }}
  .back {{ display:inline-block; margin-bottom:18px; color:rgba(255,255,255,.7); font-size:13px; text-decoration:none; }}
  .foot {{ margin-top:36px; font-size:12px; color:rgba(255,255,255,0.35); }}
</style>
</head>
<body>
  <div class="wrap">
    <a class="back" href="../">← Назад до звітів Муза</a>
    <div class="badge"><span class="dot"></span> Bolt Food · Weekly</div>
    <h1>Щотижневі витрати на промо</h1>
    <p class="sub">Муза / Європіано · Bolt vs заклад · по локаціях і по замовленнях</p>
    <ul class="list">
{lis}
    </ul>
    <p class="foot">Оновлення щопонеділка · попередній повний тиждень (Пн–Нд)</p>
  </div>
</body>
</html>
""", encoding="utf-8")


def monday_of(week_start: pd.Timestamp) -> dt.date:
    d = pd.Timestamp(week_start).date()
    return d - dt.timedelta(days=d.weekday())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--run-date", default=None, help="YYYY-MM-DD, defaults to today UTC")
    ap.add_argument("--only", default=None, help="Skip unless this includes muza")
    ap.add_argument("--backfill-from", default=None, help="YYYY-MM-DD Monday (or any day in that week)")
    args = ap.parse_args()

    if args.only:
        keys = {x.strip() for x in args.only.split(",") if x.strip()}
        if keys and "muza" not in keys:
            print("Skipping Muza promo spend (--only does not include muza)")
            return

    run_date = (
        dt.date.fromisoformat(args.run_date)
        if args.run_date
        else dt.datetime.utcnow().date()
    )
    last_start, last_end = prev_full_week(run_date)
    if args.backfill_from:
        first = dt.date.fromisoformat(args.backfill_from)
        first = first - dt.timedelta(days=first.weekday())
    else:
        first = last_start
    weeks = weeks_in_range(first, last_start)
    print(f"Promo spend weeks: {weeks[0][0]} → {weeks[-1][1]}  ({len(weeks)} weeks)")

    providers = promo_providers()
    ids_str = ",".join(str(p) for p in providers)
    range_start, range_end = weeks[0][0], weeks[-1][1]
    repo_root = Path(args.repo_root)
    out_dir = repo_root / FOLDER
    style, logo_uri = load_assets(repo_root)

    with DBX() as dbx:
        loc = dbx.query(f"""
            SELECT
              provider_id,
              order_created_date_local AS order_date,
              COUNT(*) AS delivered,
              SUM(order_gmv_eur) AS gmv_eur,
              SUM(COALESCE(campaign_spend_bolt_eur, 0)) AS bolt_promo_eur,
              SUM(COALESCE(campaign_spend_provider_eur, 0)) AS part_promo_eur,
              SUM(CASE WHEN COALESCE(campaign_spend_bolt_eur,0) > 0
                         OR COALESCE(campaign_spend_provider_eur,0) > 0 THEN 1 ELSE 0 END) AS promo_ord
            FROM main.ng_delivery.dim_order_delivery
            WHERE provider_id IN ({ids_str})
              AND order_state = 'delivered'
              AND order_created_date_local >= DATE('{range_start.isoformat()}')
              AND order_created_date_local <= DATE('{range_end.isoformat()}')
            GROUP BY provider_id, order_created_date_local
        """)
        orders = dbx.query(f"""
            SELECT
              provider_id,
              COALESCE(order_reference_id, CAST(order_id AS STRING)) AS order_code,
              order_id,
              order_created_date_local AS order_date,
              order_gmv_eur,
              COALESCE(order_gmv_local, order_gmv_eur * {UAH}) AS order_gmv_uah,
              COALESCE(campaign_spend_bolt_eur, 0) AS bolt_promo_eur,
              COALESCE(campaign_spend_provider_eur, 0) AS part_promo_eur
            FROM main.ng_delivery.dim_order_delivery
            WHERE provider_id IN ({ids_str})
              AND order_state = 'delivered'
              AND order_created_date_local >= DATE('{range_start.isoformat()}')
              AND order_created_date_local <= DATE('{range_end.isoformat()}')
              AND (COALESCE(campaign_spend_bolt_eur, 0) > 0
                   OR COALESCE(campaign_spend_provider_eur, 0) > 0)
        """)
    print(f"  daily loc rows: {len(loc)}; promo orders: {len(orders)}")

    if not loc.empty:
        loc["week_mon"] = pd.to_datetime(loc["order_date"]).dt.date.map(
            lambda d: d - dt.timedelta(days=d.weekday())
        )
    if not orders.empty:
        orders["week_mon"] = pd.to_datetime(orders["order_date"]).dt.date.map(
            lambda d: d - dt.timedelta(days=d.weekday())
        )

    for start, end in weeks:
        loc_week = pd.DataFrame(columns=["delivered", "gmv_eur", "bolt_promo_eur", "part_promo_eur", "promo_ord"])
        if not loc.empty:
            sub = loc[loc["week_mon"] == start]
            if not sub.empty:
                loc_week = sub.groupby("provider_id")[
                    ["delivered", "gmv_eur", "bolt_promo_eur", "part_promo_eur", "promo_ord"]
                ].sum()
        orders_week = pd.DataFrame()
        if not orders.empty:
            orders_week = orders[orders["week_mon"] == start].copy()
        render_week(providers, loc_week, orders_week, start, end, style, logo_uri, out_dir)

    rebuild_index(out_dir)
    print(f"Wrote {len(weeks)} promo-spend report(s) to {out_dir}")


if __name__ == "__main__":
    main()

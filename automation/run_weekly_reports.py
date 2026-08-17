#!/usr/bin/env python3
"""
Weekly partner report runner.

Computes "the previous fully-completed week" (Mon–Sun) relative to the
run date, pulls metrics from Databricks for every provider registered in
partners_config.PARTNERS, renders one HTML report per location (same
template as the existing Salateira weekly reports), and writes:

  {repo_root}/{github_folder}/{YYYY-MM-DD_DD}/{Location}.html
  {repo_root}/{github_folder}/{YYYY-MM-DD_DD}/index.html   (week index)
  {repo_root}/{github_folder}/index.html                    (root: list of weeks)

Intended to run inside a GitHub Actions job that has already checked out
the nataliiaklymas-cpu/reports repo — this script only writes files;
committing/pushing is done by the workflow.

Local testing:
    python3 run_weekly_reports.py --repo-root /path/to/local/checkout --run-date 2026-07-27

Without --run-date, "today" (UTC) is used, so in production this always
targets the week that ended yesterday (the script is scheduled for Monday).
"""
import argparse
import datetime
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dbx import DBX
from partners_config import PARTNERS
from report_template import build_report, build_network_summary

DAY_NAMES_UA = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


def slugify(name: str) -> str:
    s = re.sub(r"[^\w]+", "_", name, flags=re.UNICODE).strip("_")
    return s


def compute_week(run_date: datetime.date):
    """Previous fully-completed Mon–Sun week relative to run_date."""
    weekday = run_date.weekday()  # Monday=0
    this_monday = run_date - datetime.timedelta(days=weekday)
    cur_mon = this_monday - datetime.timedelta(days=7)
    cur_end = this_monday  # exclusive upper bound (== start of run week)
    prev_mon = cur_mon - datetime.timedelta(days=7)
    cur_sun = cur_end - datetime.timedelta(days=1)

    months_ua = ["", "січня", "лютого", "березня", "квітня", "травня", "червня",
                 "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    months_ua_short = ["", "січ", "лют", "бер", "кві", "трав", "черв",
                        "лип", "серп", "вер", "жовт", "лист", "груд"]

    if cur_mon.month == cur_sun.month:
        period_label = f"{cur_mon.day}–{cur_sun.day} {months_ua[cur_sun.month]} {cur_sun.year}"
        period_short = f"{cur_mon.day}–{cur_sun.day} {months_ua_short[cur_sun.month]}"
    else:
        period_label = (f"{cur_mon.day} {months_ua[cur_mon.month]} – "
                         f"{cur_sun.day} {months_ua[cur_sun.month]} {cur_sun.year}")
        period_short = (f"{cur_mon.day} {months_ua_short[cur_mon.month]} – "
                         f"{cur_sun.day} {months_ua_short[cur_sun.month]}")

    prev_sun = cur_mon - datetime.timedelta(days=1)
    prev_label = f"{prev_mon.day}–{prev_sun.day} {months_ua_short[prev_sun.month]}"

    days_ua = [f"{DAY_NAMES_UA[i]}<br>{(cur_mon + datetime.timedelta(days=i)).strftime('%d.%m')}" for i in range(7)]
    days_iso = [(cur_mon + datetime.timedelta(days=i)).isoformat() for i in range(7)]

    week_folder = f"{cur_mon.isoformat()}_{cur_sun.strftime('%d')}"

    return dict(
        cur_mon=cur_mon.isoformat(), cur_end=cur_end.isoformat(), prev_mon=prev_mon.isoformat(),
        period_label=period_label, period_short=period_short, prev_label=prev_label,
        days_ua=days_ua, days_iso=days_iso, week_folder=week_folder,
    )


def sf(v, d=0):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return d
    return v


def row(df, pid):
    r = df[df["provider_id"] == pid]
    return r.iloc[0].to_dict() if not r.empty else {}


ROOT_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{display_name} — Weekly Reports</title>
<style>
  :root {{ --green:#34D186; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #fff; min-height: 100vh; padding: 56px 24px;
    background: radial-gradient(1000px 700px at 15% 5%, #1b6b47 0%, transparent 58%), radial-gradient(900px 650px at 95% 95%, #0e3d2a 0%, transparent 55%), linear-gradient(135deg, #0c1f16 0%, #0a1712 100%); }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  .badge {{ display:inline-flex; align-items:center; gap:8px; background:rgba(52,209,134,0.15); color:var(--green); border:1px solid rgba(52,209,134,0.35); padding:6px 13px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.3px; margin-bottom:18px; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:var(--green); }}
  h1 {{ font-size:34px; font-weight:800; letter-spacing:-.5px; margin-bottom:6px; }}
  .sub {{ color:rgba(255,255,255,0.6); font-size:15px; margin-bottom:30px; }}
  .list {{ list-style:none; display:flex; flex-direction:column; gap:12px; }}
  .list a {{ display:flex; align-items:center; justify-content:space-between; gap:16px; text-decoration:none; color:#fff;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:18px 20px; transition:all .18s; }}
  .list a:hover {{ background:rgba(52,209,134,0.12); border-color:rgba(52,209,134,0.4); }}
  .list .t {{ font-weight:600; font-size:16px; }}
  .list .count {{ color:rgba(255,255,255,0.4); font-weight:400; font-size:13px; }}
  .foot {{ margin-top:36px; font-size:12px; color:rgba(255,255,255,0.35); }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="badge"><span class="dot"></span> Bolt Food · Weekly Reports</div>
    <h1>{display_name} — Weekly Reports</h1>
    <p class="sub">Щотижневі звіти по локаціях</p>
    <ul class="list">
{items}
    </ul>
    <div class="foot">Bolt Food · конфіденційно для партнера</div>
  </div>
</body>
</html>
"""

WEEK_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{display_name} — Weekly {period_short} 2026</title>
<style>
  :root {{ --green:#34D186; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #fff; min-height: 100vh; padding: 56px 24px;
    background: radial-gradient(1000px 700px at 15% 5%, #1b6b47 0%, transparent 58%), radial-gradient(900px 650px at 95% 95%, #0e3d2a 0%, transparent 55%), linear-gradient(135deg, #0c1f16 0%, #0a1712 100%); }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  .badge {{ display:inline-flex; align-items:center; gap:8px; background:rgba(52,209,134,0.15); color:var(--green); border:1px solid rgba(52,209,134,0.35); padding:6px 13px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.3px; margin-bottom:18px; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:var(--green); }}
  a.back {{ color:rgba(255,255,255,0.55); text-decoration:none; font-size:14px; display:inline-block; margin-bottom:16px; }}
  a.back:hover {{ color:#fff; }}
  h1 {{ font-size:30px; font-weight:800; letter-spacing:-.5px; margin-bottom:6px; }}
  .sub {{ color:rgba(255,255,255,0.6); font-size:15px; margin-bottom:30px; }}
  .list {{ list-style:none; display:flex; flex-direction:column; gap:12px; }}
  .list a {{ display:flex; align-items:center; justify-content:space-between; gap:16px; text-decoration:none; color:#fff;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:16px 20px; transition:all .18s; }}
  .list a:hover {{ background:rgba(52,209,134,0.12); border-color:rgba(52,209,134,0.4); }}
  .list .t {{ font-weight:600; font-size:16px; }}
  .list .count {{ color:rgba(255,255,255,0.4); font-weight:400; font-size:13px; }}
  .foot {{ margin-top:36px; font-size:12px; color:rgba(255,255,255,0.35); }}
</style>
</head>
<body>
  <div class="wrap">
    <a class="back" href="../">← Усі тижні</a>
    <div class="badge"><span class="dot"></span> Bolt Food · Weekly Reports</div>
    <h1>{display_name} · {period_label}</h1>
    <p class="sub">Звіти по локаціях ({count})</p>
    <ul class="list">
{items}
    </ul>
    <div class="foot">Bolt Food · конфіденційно для партнера</div>
  </div>
</body>
</html>
"""


def run_partner(partner_key: str, cfg: dict, week: dict, repo_root: str):
    providers = cfg["providers"]
    ids_str = ",".join(str(p) for p in providers)
    display_name = cfg["display_name"]
    emoji = cfg["emoji"]
    github_folder = cfg["github_folder"]

    print(f"\n=== {display_name} ({len(providers)} locations) — {week['period_label']} ===")

    with DBX() as dbx:
        cur_df = dbx.query(f"""
            SELECT provider_id,
                failed_orders_count AS failed,
                total_gmv_before_discounts_eur AS gmv_eur,
                total_campaign_spend_bolt_eur AS bolt_promo,
                campaign_orders_count AS promo_ord,
                delivered_bolt_plus_orders_count AS bp_ord,
                users_activated_provider_count AS new_u,
                provider_rating_per_order_value AS rating,
                provider_acceptance_minutes_per_order_value AS accept_min,
                provider_processing_minutes_per_order_value AS prep_min,
                bad_provider_rating_rate_value AS bad_rt,
                provider_active_rate_value AS avail
            FROM ng_delivery_spark.fact_provider_weekly
            WHERE provider_id IN ({ids_str})
              AND metric_timestamp_partition = DATE('{week["cur_mon"]}')
        """)
        prev_df = dbx.query(f"""
            SELECT provider_id,
                total_gmv_before_discounts_eur AS gmv_eur
            FROM ng_delivery_spark.fact_provider_weekly
            WHERE provider_id IN ({ids_str})
              AND metric_timestamp_partition = DATE('{week["prev_mon"]}')
        """)
        total_del_cur_df = dbx.query(f"""
            SELECT provider_id, COUNT(*) AS delivered_total
            FROM ng_delivery_spark.dim_order_delivery
            WHERE provider_id IN ({ids_str})
              AND order_created_date_local >= DATE('{week["cur_mon"]}') AND order_created_date_local < DATE('{week["cur_end"]}')
              AND order_state = 'delivered'
            GROUP BY provider_id
        """)
        total_del_prev_df = dbx.query(f"""
            SELECT provider_id, COUNT(*) AS delivered_total
            FROM ng_delivery_spark.dim_order_delivery
            WHERE provider_id IN ({ids_str})
              AND order_created_date_local >= DATE('{week["prev_mon"]}') AND order_created_date_local < DATE('{week["cur_mon"]}')
              AND order_state = 'delivered'
            GROUP BY provider_id
        """)
        daily_df = dbx.query(f"""
            SELECT provider_id, order_created_date_local AS day,
                COUNT(CASE WHEN order_state='delivered' THEN 1 END) AS delivered
            FROM ng_delivery_spark.dim_order_delivery
            WHERE provider_id IN ({ids_str})
              AND order_created_date_local >= DATE('{week["cur_mon"]}')
              AND order_created_date_local < DATE('{week["cur_end"]}')
            GROUP BY provider_id, order_created_date_local
        """)
        dish_df = dbx.query(f"""
            SELECT provider_id, basket_item_name, COUNT(*) AS qty
            FROM ng_delivery_spark.dim_basket_item_delivery
            WHERE provider_id IN ({ids_str})
              AND order_created_date_local >= DATE('{week["cur_mon"]}')
              AND order_created_date_local < DATE('{week["cur_end"]}')
              AND basket_item_name IS NOT NULL AND basket_item_name != ''
              AND menu_item_type = 'dish'
            GROUP BY provider_id, basket_item_name
            ORDER BY provider_id, qty DESC
        """)
        rat_df = dbx.query(f"""
            SELECT provider_id,
                ROUND(AVG(rating_value),2) AS avg_rating,
                COUNT(*) AS review_cnt,
                SUM(CASE WHEN rating_value<=2 THEN 1 ELSE 0 END) AS bad_cnt
            FROM ng_delivery_spark.delivery_rating_provider_rating_history
            WHERE provider_id IN ({ids_str})
              AND created_date >= DATE('{week["cur_mon"]}') AND created_date < DATE('{week["cur_end"]}')
            GROUP BY provider_id
        """)
        cmt_df = dbx.query(f"""
            SELECT provider_id, rating_value AS rating, comment
            FROM ng_delivery_spark.delivery_rating_provider_rating_history
            WHERE provider_id IN ({ids_str})
              AND created_date >= DATE('{week["cur_mon"]}') AND created_date < DATE('{week["cur_end"]}')
              AND comment IS NOT NULL AND TRIM(comment) != ''
            ORDER BY provider_id, rating_value DESC
        """)

    week_dir = os.path.join(repo_root, github_folder, week["week_folder"])
    os.makedirs(week_dir, exist_ok=True)

    week_items = []
    loc_results = []
    for pid, meta in providers.items():
        name = meta["name"]
        brand_label = meta.get("brand", display_name)
        city = meta.get("city", "Київ")

        daily_map = {}
        sub = daily_df[daily_df["provider_id"] == pid]
        for _, r in sub.iterrows():
            daily_map[str(r["day"])[:10]] = int(sf(r["delivered"]))

        dishes = [str(r["basket_item_name"]) for _, r in dish_df[dish_df["provider_id"] == pid].head(5).iterrows()]

        cm = cmt_df[cmt_df["provider_id"] == pid]
        pos = [(int(x["rating"]), str(x["comment"])[:220]) for _, x in cm[cm["rating"] >= 4].head(2).iterrows()]
        neg = [(int(x["rating"]), str(x["comment"])[:220]) for _, x in cm[cm["rating"] <= 2].head(2).iterrows()]

        html, stats = build_report(
            pid=pid, name=name, brand_label=brand_label, partner_emoji=emoji, city=city,
            period_label=week["period_label"], period_short=week["period_short"], prev_label=week["prev_label"],
            days_ua=week["days_ua"], days_iso=week["days_iso"],
            cur_row=row(cur_df, pid), prev_row=row(prev_df, pid),
            delivered_total=row(total_del_cur_df, pid).get("delivered_total", 0),
            prev_delivered_total=row(total_del_prev_df, pid).get("delivered_total", 0),
            daily_map=daily_map, dishes=dishes,
            rating_row=row(rat_df, pid), comments_pos=pos, comments_neg=neg,
        )

        short_name = name.replace(brand_label, "").strip()
        slug = slugify(short_name)
        fname = f"{brand_label.replace(' ', '_')}_{slug}_{week['week_folder']}.html".replace("__", "_")
        with open(os.path.join(week_dir, fname), "w", encoding="utf-8") as f:
            f.write(html)
        week_items.append((fname, short_name, pid))
        loc_results.append(dict(pid=pid, name=name, short_name=short_name, city=city, fname=fname, stats=stats))
        print(f"  ok {pid} {name:45s} {stats['delivered']:>4} zam  {stats['gmv']:>8,} UAH".replace(",", " "))

    # Network-wide total summary (all locations combined)
    total_fname = f"{display_name.replace(' ', '_')}_TOTAL_{week['week_folder']}.html"
    total_html, total_stats = build_network_summary(
        display_name=display_name, emoji=emoji, brand_color=cfg.get("brand_color", "#2AAF6D"),
        period_label=week["period_label"], period_short=week["period_short"], prev_label=week["prev_label"],
        days_ua=week["days_ua"], days_iso=week["days_iso"], loc_results=loc_results,
    )
    with open(os.path.join(week_dir, total_fname), "w", encoding="utf-8") as f:
        f.write(total_html)
    print(f"  -> TOTAL {display_name:20s} {total_stats['delivered']:>5} zam  {total_stats['gmv']:>9,} UAH".replace(",", " "))

    items_html = (
        f'      <li><a href="{total_fname}" style="border-color:rgba(255,165,0,.35);background:rgba(255,165,0,.08);">'
        f'<span class="t">🌐 Мережа тотал</span><span class="count">{len(week_items)} локацій</span></a></li>\n'
    ) + "\n".join(
        f'      <li><a href="{fname}"><span class="t">{short}</span><span class="count">#{pid}</span></a></li>'
        for fname, short, pid in week_items
    )
    with open(os.path.join(week_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(WEEK_INDEX_TEMPLATE.format(
            display_name=display_name, period_short=week["period_short"], period_label=week["period_label"],
            count=len(week_items), items=items_html,
        ))

    root_dir = os.path.join(repo_root, github_folder)
    root_index_path = os.path.join(root_dir, "index.html")
    week_entry = (
        f'      <li><a href="{week["week_folder"]}/"><span class="t">{week["period_label"]}</span>'
        f'<span class="count">{len(week_items)} локацій</span></a></li>'
    )
    existing_entries = []
    if os.path.exists(root_index_path):
        with open(root_index_path, "r", encoding="utf-8") as f:
            existing_html = f.read()
        for m in re.finditer(r'<li><a href="([^/]+)/">.*?</a></li>', existing_html):
            if m.group(1) != week["week_folder"]:
                existing_entries.append("      " + m.group(0))
    all_entries = [week_entry] + existing_entries  # newest first
    with open(root_index_path, "w", encoding="utf-8") as f:
        f.write(ROOT_INDEX_TEMPLATE.format(display_name=display_name, items="\n".join(all_entries)))

    print(f"  -> {len(week_items)} reports written to {week_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to the checked-out reports repo")
    ap.add_argument("--run-date", default=None, help="Override run date (YYYY-MM-DD), for testing")
    ap.add_argument("--only", default=None, help="Comma-separated partner keys to run (default: all)")
    args = ap.parse_args()

    run_date = (
        datetime.date.fromisoformat(args.run_date)
        if args.run_date
        else datetime.datetime.utcnow().date()
    )
    week = compute_week(run_date)
    print(f"Run date: {run_date.isoformat()}  ->  target week: {week['period_label']} ({week['week_folder']})")

    only = set(args.only.split(",")) if args.only else None
    for key, cfg in PARTNERS.items():
        if only and key not in only:
            continue
        run_partner(key, cfg, week, args.repo_root)

    print("\nAll done.")


if __name__ == "__main__":
    main()

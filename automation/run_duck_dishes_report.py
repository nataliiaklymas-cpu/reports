#!/usr/bin/env python3
"""Weekly internal report for Chornomorka duck dishes (provider 5092622)."""

import argparse
import datetime as dt
import html
import os
import re
from pathlib import Path

import pandas as pd

from dbx import DBX


PROVIDER_ID = 5092622
STANDARD_COMMISSION_RATE = 0.15
OUTPUT_FOLDER = Path("internal/chornomorka-duck-dishes")
ALLOWED_RUN_DATES = {
    dt.date(2026, 9, 28),
    dt.date(2026, 10, 5),
    dt.date(2026, 10, 12),
    dt.date(2026, 10, 19),
    dt.date(2026, 10, 26),
    dt.date(2026, 11, 2),
}
DISH_CASE_SQL = """
CASE
  WHEN trim(lower(basket_item_name)) = 'качине олів''є'
    THEN 'Качине олів''є'
  WHEN trim(lower(basket_item_name)) = 'фірмовий борщ з качкою'
    THEN 'Фірмовий борщ з качкою'
  WHEN trim(lower(basket_item_name)) = 'домашня котлета з качки з картопляним пюре та маринованими томатами'
    THEN 'Домашня котлета з качки з картопляним пюре та маринованими томатами'
  WHEN trim(lower(basket_item_name)) = 'конфі з качиної ніжки з тушкованою капустою'
    THEN 'Конфі з качиної ніжки з тушкованою капустою'
END
"""
DISH_FILTER_SQL = f"({DISH_CASE_SQL.strip()}) IS NOT NULL"


def week_for(run_date: dt.date):
    monday = run_date - dt.timedelta(days=run_date.weekday() + 7)
    end = monday + dt.timedelta(days=7)
    sunday = end - dt.timedelta(days=1)
    return monday, end, sunday


def money(value):
    if pd.isna(value):
        return "—"
    return f"{float(value):,.2f}".replace(",", " ")


def integer(value):
    if pd.isna(value):
        return "0"
    return f"{int(value):,}".replace(",", " ")


def esc(value):
    if value is None or pd.isna(value):
        return "—"
    return html.escape(str(value))


def load_data(monday: dt.date, end: dt.date):
    with DBX() as dbx:
        items = dbx.query(
            f"""
            SELECT
              b.order_id,
              {DISH_CASE_SQL} AS dish,
              b.basket_item_name AS source_dish_name,
              b.basket_item_amount AS quantity,
              CAST(b.item_price_before_discount_with_vat_local AS DOUBLE) AS dish_before_discount_uah,
              CAST(b.item_price_after_discount_with_vat_local AS DOUBLE) AS dish_after_discount_uah,
              CAST(b.provider_price_after_discount_local AS DOUBLE) AS duck_commission_base_uah
            FROM main.ng_delivery.dim_basket_item_delivery b
            WHERE b.provider_id = {PROVIDER_ID}
              AND b.order_created_date_local >= DATE('{monday.isoformat()}')
              AND b.order_created_date_local < DATE('{end.isoformat()}')
              AND b.menu_item_type = 'dish'
              AND {DISH_FILTER_SQL}
            """
        )

        orders = dbx.query(
            f"""
            SELECT
              o.order_id,
              o.order_reference_id AS order_code,
              o.order_created_ts_local AS ordered_at,
              o.order_state,
              CAST(o.order_gmv_local AS DOUBLE) AS order_before_discount_uah,
              CAST(o.order_gmv_after_discount_local AS DOUBLE) AS order_after_discount_uah,
              CAST(o.total_order_item_discount_local AS DOUBLE) AS order_discount_uah,
              CAST(m.bolt_menu_campaign_cost_eur AS DOUBLE) AS bolt_discount_eur,
              CAST(m.provider_menu_campaign_cost_eur AS DOUBLE) AS provider_discount_eur
            FROM main.ng_delivery.dim_order_delivery o
            LEFT JOIN main.ng_public.etl_delivery_order_monetary_metrics m
              ON o.order_id = m.order_id
            WHERE o.provider_id = {PROVIDER_ID}
              AND o.order_created_date_local >= DATE('{monday.isoformat()}')
              AND o.order_created_date_local < DATE('{end.isoformat()}')
            """
        )

    if items.empty:
        return empty_details(), empty_summary()

    details = items.merge(orders, on="order_id", how="left")
    details["quantity"] = details["quantity"].fillna(0).astype(int)
    details["status"] = details["order_state"].map(
        lambda x: "Доставлено" if x == "delivered" else "Скасовано"
    )
    details["discount_payer"] = details.apply(discount_payer, axis=1)
    details["standard_commission_rate_pct"] = STANDARD_COMMISSION_RATE * 100
    delivered = details["order_state"].eq("delivered")
    details["standard_commission_duck_uah"] = (
        details["duck_commission_base_uah"]
        * STANDARD_COMMISSION_RATE
    ).where(delivered, 0)
    details["commission_10pct_duck_uah"] = (
        details["duck_commission_base_uah"] * 0.10
    ).where(delivered, 0)
    details["commission_adjustment_uah"] = (
        details["standard_commission_duck_uah"]
        - details["commission_10pct_duck_uah"]
    )

    summary = (
        details.groupby(["dish", "status"], as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            orders=("order_id", "nunique"),
            duck_sales_after_discount_uah=("dish_after_discount_uah", "sum"),
            standard_commission_duck_uah=("standard_commission_duck_uah", "sum"),
            commission_10pct_duck_uah=("commission_10pct_duck_uah", "sum"),
            commission_adjustment_uah=("commission_adjustment_uah", "sum"),
        )
    )
    details = details.sort_values(["ordered_at", "order_code", "dish"])
    return details, summary


def discount_payer(row):
    bolt = float(row.get("bolt_discount_eur") or 0)
    provider = float(row.get("provider_discount_eur") or 0)
    if bolt > 0 and provider > 0:
        return "Bolt + партнер"
    if bolt > 0:
        return "Bolt"
    if provider > 0:
        return "Партнер"
    return "Без знижки"


def empty_details():
    return pd.DataFrame(
        columns=[
            "order_code", "ordered_at", "status", "dish", "source_dish_name",
            "quantity", "dish_before_discount_uah", "dish_after_discount_uah",
            "order_before_discount_uah", "order_after_discount_uah",
            "order_discount_uah", "discount_payer",
            "standard_commission_rate_pct", "standard_commission_duck_uah",
            "commission_10pct_duck_uah", "commission_adjustment_uah",
        ]
    )


def empty_summary():
    return pd.DataFrame(
        columns=[
            "dish", "status", "quantity", "orders",
            "duck_sales_after_discount_uah",
            "standard_commission_duck_uah",
            "commission_10pct_duck_uah", "commission_adjustment_uah",
        ]
    )


def build_html(details, summary, monday, sunday, xlsx_name, is_demo=False):
    delivered_qty = details.loc[details["status"].eq("Доставлено"), "quantity"].sum()
    cancelled_qty = details.loc[details["status"].eq("Скасовано"), "quantity"].sum()
    delivered_orders = details.loc[
        details["status"].eq("Доставлено"), "order_id"
    ].nunique() if "order_id" in details else 0
    adjustment = details["commission_adjustment_uah"].sum() if not details.empty else 0

    summary_rows = "".join(
        f"""<tr><td>{esc(r.dish)}</td><td><span class="status {'ok' if r.status == 'Доставлено' else 'bad'}">{esc(r.status)}</span></td>
        <td class="num">{integer(r.quantity)}</td><td class="num">{integer(r.orders)}</td>
        <td class="num">{money(r.duck_sales_after_discount_uah)}</td>
        <td class="num">{money(r.standard_commission_duck_uah)}</td>
        <td class="num">{money(r.commission_10pct_duck_uah)}</td>
        <td class="num">{money(r.commission_adjustment_uah)}</td></tr>"""
        for r in summary.itertuples()
    ) or '<tr><td colspan="8" class="empty">За цей тиждень замовлень із цими стравами немає.</td></tr>'

    detail_rows = "".join(
        f"""<tr><td class="num">{esc(r.order_code)}</td><td>{esc(pd.to_datetime(r.ordered_at).strftime('%d.%m %H:%M') if not pd.isna(r.ordered_at) else None)}</td>
        <td><span class="status {'ok' if r.status == 'Доставлено' else 'bad'}">{esc(r.status)}</span></td>
        <td>{esc(r.dish)}</td><td class="num">{integer(r.quantity)}</td>
        <td class="num">{money(r.order_before_discount_uah)}</td><td class="num">{money(r.order_after_discount_uah)}</td>
        <td>{esc(r.discount_payer)}</td><td class="num">{money(r.standard_commission_rate_pct)}%</td>
        <td class="num">{money(r.standard_commission_duck_uah)}</td>
        <td class="num">{money(r.commission_10pct_duck_uah)}</td><td class="num">{money(r.commission_adjustment_uah)}</td></tr>"""
        for r in details.itertuples()
    ) or '<tr><td colspan="12" class="empty">Деталей замовлень немає.</td></tr>'

    demo_banner = (
        '<div class="demo">Демо · дані вигадані · не використовувати для виплат</div>'
        if is_demo else ""
    )
    return f"""<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Качині страви Чорноморки · {monday:%d.%m}–{sunday:%d.%m.%Y}</title>
<style>
@font-face{{font-family:InterVariable;src:url("https://static.bolt.eu/fonts/inter/InterVariable.woff2") format("woff2");font-weight:100 900;font-display:swap}}
:root{{--floor:#eef1f0;--card:#fff;--text:#191f1c;--muted:#5f6563;--green:#2a9c64;--green-dark:#0c2c1c;--green-soft:#e7f6ed;--red:#b20f1c;--red-soft:#ffeaea;--separator:rgba(0,45,30,.07);--radius:16px;--pill:600rem}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--floor);color:var(--text);font-family:InterVariable,Inter,sans-serif;font-feature-settings:"cv03","cv04";padding:32px 24px 64px}}main{{max-width:1400px;margin:auto}}
header{{background:var(--green-dark);color:white;border-radius:var(--radius);padding:32px;margin-bottom:8px}}.demo{{background:var(--red-soft);color:var(--red);border-radius:var(--pill);display:inline-flex;padding:8px 12px;font-size:12px;font-weight:650;margin-bottom:16px}}.caps{{font-size:11px;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:var(--green-soft)}}h1{{font-size:32px;line-height:1.2;margin:8px 0}}header p{{color:var(--green-soft);margin:0}}.actions{{margin-top:24px}}
.button{{display:inline-flex;min-height:48px;align-items:center;padding:0 20px;border-radius:var(--pill);background:var(--green);color:white;text-decoration:none;font-weight:650}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:8px}}.card{{background:var(--card);border-radius:var(--radius);padding:20px}}.label{{font-size:13px;color:var(--muted)}}.value{{font-size:28px;font-weight:650;font-variant-numeric:tabular-nums;margin-top:4px}}
section{{background:var(--card);border-radius:var(--radius);padding:24px;margin-top:8px}}h2{{font-size:22px;margin:0 0 4px}}.note{{color:var(--muted);font-size:13px;margin:0 0 20px}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:900px}}th{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);text-align:left;padding:10px 8px;border-bottom:1px solid var(--separator)}}td{{padding:12px 8px;border-bottom:1px solid var(--separator);font-size:13px}}.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}.status{{display:inline-block;padding:5px 9px;border-radius:var(--pill);font-weight:650;font-size:11px}}.ok{{background:var(--green-soft);color:var(--green-dark)}}.bad{{background:var(--red-soft);color:var(--red)}}.empty{{text-align:center;color:var(--muted);padding:40px}}footer{{color:var(--muted);font-size:12px;padding:20px 4px}}
@media(max-width:760px){{body{{padding:16px 12px 40px}}header{{padding:24px}}.grid{{grid-template-columns:1fr 1fr}}.value{{font-size:22px}}}}
</style></head><body><main>
<header>{demo_banner}<div class="caps">Bolt Food · Internal</div><h1>Качині страви Чорноморки</h1>
<p>Provider {PROVIDER_ID} · {monday:%d.%m.%Y}–{sunday:%d.%m.%Y}</p>
<div class="actions"><a class="button" href="{xlsx_name}" download>Завантажити Excel</a></div></header>
<div class="grid"><div class="card"><div class="label">Продано страв</div><div class="value">{integer(delivered_qty)}</div></div>
<div class="card"><div class="label">Доставлених замовлень</div><div class="value">{integer(delivered_orders)}</div></div>
<div class="card"><div class="label">Скасовано страв</div><div class="value">{integer(cancelled_qty)}</div></div>
<div class="card"><div class="label">Коригування до виплати, грн</div><div class="value">{money(adjustment)}</div></div></div>
<section><h2>Підсумок по стравах</h2><p class="note">Комісія 10% та коригування рахуються лише для доставлених качиних страв.</p>
<div class="scroll"><table><thead><tr><th>Страва</th><th>Статус</th><th class="num">Кількість</th><th class="num">Замовлення</th><th class="num">Продажі, грн</th><th class="num">Стандартна комісія, грн</th><th class="num">Комісія 10%, грн</th><th class="num">До виплати, грн</th></tr></thead><tbody>{summary_rows}</tbody></table></div></section>
<section><h2>Перелік замовлень</h2><p class="note">Вартість замовлення — GMV страв до та після меню-знижки. Платник знижки визначається за фактичними campaign cost.</p>
<div class="scroll"><table><thead><tr><th>Код</th><th>Час</th><th>Статус</th><th>Страва</th><th class="num">К-сть</th><th class="num">До знижки</th><th class="num">Після знижки</th><th>Платник</th><th class="num">Станд. ставка</th><th class="num">Станд. комісія</th><th class="num">10%</th><th class="num">До виплати</th></tr></thead><tbody>{detail_rows}</tbody></table></div></section>
<footer>Розрахунок “до виплати” = стандартна комісія 15% на качині страви мінус комісія 10% на ці страви. Інші позиції в чеку не враховані.</footer>
</main></body></html>"""


def write_excel(path, details, summary, monday, sunday, is_demo=False):
    rename_summary = {
        "dish": "Страва", "status": "Статус", "quantity": "Кількість страв",
        "orders": "Кількість замовлень",
        "duck_sales_after_discount_uah": "Продажі качиних страв після знижки, грн",
        "standard_commission_duck_uah": "Стандартна комісія, грн",
        "commission_10pct_duck_uah": "Комісія 10%, грн",
        "commission_adjustment_uah": "До виплати, грн",
    }
    detail_columns = {
        "order_code": "Код замовлення", "ordered_at": "Дата і час",
        "status": "Статус", "dish": "Страва",
        "source_dish_name": "Назва в системі", "quantity": "Кількість",
        "dish_before_discount_uah": "Страва до знижки, грн",
        "dish_after_discount_uah": "Страва після знижки, грн",
        "order_before_discount_uah": "Замовлення до знижки, грн",
        "order_after_discount_uah": "Замовлення після знижки, грн",
        "order_discount_uah": "Знижка замовлення, грн",
        "discount_payer": "Платник знижки",
        "standard_commission_rate_pct": "Стандартна ставка, %",
        "standard_commission_duck_uah": "Стандартна комісія на качині страви, грн",
        "commission_10pct_duck_uah": "Комісія 10% на качині страви, грн",
        "commission_adjustment_uah": "До виплати, грн",
    }
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        summary.rename(columns=rename_summary).to_excel(writer, sheet_name="Підсумок", index=False)
        details[[c for c in detail_columns if c in details]].rename(
            columns=detail_columns
        ).to_excel(writer, sheet_name="Замовлення", index=False)
        info_rows = []
        if is_demo:
            info_rows.append(("Статус", "ДЕМО — дані вигадані, не використовувати для виплат"))
        info_rows.extend(
            [
                ("Provider ID", PROVIDER_ID),
                ("Період", f"{monday:%d.%m.%Y}–{sunday:%d.%m.%Y}"),
                (
                    "Формула виплати",
                    "Комісія 15% на качині страви мінус комісія 10% на качині страви",
                ),
            ]
        )
        info = pd.DataFrame(info_rows, columns=["Параметр", "Значення"])
        info.to_excel(writer, sheet_name="Методологія", index=False)
        for sheet in writer.book.worksheets:
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for column in sheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in column) + 2, 48)
                sheet.column_dimensions[column[0].column_letter].width = width


def rebuild_root_index(root):
    entries = []
    for folder in sorted(
        [p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}", p.name)],
        reverse=True,
    ):
        report = next(folder.glob("*.html"), None)
        workbook = next(folder.glob("*.xlsx"), None)
        if report:
            label = folder.name.replace("_", "–")
            excel = f'<a class="excel" href="{folder.name}/{workbook.name}">Excel</a>' if workbook else ""
            entries.append(
                f'<li><a href="{folder.name}/{report.name}"><span>{label}</span><span>Відкрити</span></a>{excel}</li>'
            )
    demo_entry = (
        '<li><a href="demo/chornomorka_duck_dishes_demo.html">'
        '<span>Демо · одне уявне замовлення</span><span>Відкрити</span></a>'
        '<a class="excel" href="demo/chornomorka_duck_dishes_demo.xlsx">Excel</a></li>'
    )
    report_items = "\n".join(entries) or '<li class="empty">Реальні звіти з’являтимуться щопонеділка.</li>'
    items = demo_entry + "\n" + report_items
    content = f"""<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Качині страви Чорноморки</title>
<style>:root{{--bg:#eef1f0;--card:#fff;--text:#191f1c;--muted:#5f6563;--green:#2a9c64;--dark:#0c2c1c;--radius:16px;--pill:600rem}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,sans-serif;padding:32px 24px}}main{{max-width:760px;margin:auto}}header{{background:var(--dark);color:white;border-radius:var(--radius);padding:32px}}h1{{margin:0 0 8px;font-size:32px}}p{{margin:0;color:var(--muted)}}header p{{color:white}}ul{{list-style:none;padding:0;margin:8px 0}}li{{display:flex;gap:8px;margin-bottom:8px}}li>a:first-child{{display:flex;justify-content:space-between;flex:1;background:var(--card);padding:18px;border-radius:var(--radius);color:var(--text);text-decoration:none}}.excel{{display:flex;align-items:center;background:var(--green);color:white;padding:0 18px;border-radius:var(--pill);text-decoration:none;font-weight:650}}.empty{{background:var(--card);padding:24px;border-radius:var(--radius);color:var(--muted)}}footer{{font-size:12px;color:var(--muted);padding:16px 4px}}</style></head>
<body><main><header><h1>Качині страви Чорноморки</h1><p>Внутрішній щотижневий звіт · provider {PROVIDER_ID}</p></header><ul>{items}</ul><footer>Оновлення щопонеділка з 28.09 до 02.11.2026 включно.</footer></main></body></html>"""
    (root / "index.html").write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    run_date = dt.date.fromisoformat(args.run_date) if args.run_date else dt.datetime.utcnow().date()
    if run_date not in ALLOWED_RUN_DATES and not args.force:
        print(f"{run_date}: outside configured run dates; nothing to do.")
        return

    monday, end, sunday = week_for(run_date)
    details, summary = load_data(monday, end)
    root = Path(args.repo_root) / OUTPUT_FOLDER
    week_folder = f"{monday.isoformat()}_{sunday:%d}"
    week_dir = root / week_folder
    week_dir.mkdir(parents=True, exist_ok=True)
    base = f"chornomorka_duck_dishes_{week_folder}"
    xlsx_name = f"{base}.xlsx"
    write_excel(week_dir / xlsx_name, details, summary, monday, sunday)
    (week_dir / f"{base}.html").write_text(
        build_html(details, summary, monday, sunday, xlsx_name), encoding="utf-8"
    )
    rebuild_root_index(root)
    print(f"Wrote {len(details)} dish rows to {week_dir}")


if __name__ == "__main__":
    main()

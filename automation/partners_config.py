"""
Registry of partners with active weekly-report automation.

To onboard a new partner: add an entry to PARTNERS with its provider_id -> name/city
mapping and a couple of style params. No other code changes are needed —
run_weekly_reports.py loops over this dict.
"""

SALATEIRA_PROVIDERS = {
    173027: {"name": "Salateira Дніпровська Набережна", "brand": "Salateira", "city": "Київ"},
    173034: {"name": "Salateira вул. Лугова", "brand": "Salateira", "city": "Київ"},
    173035: {"name": "Salateira Проспект Правди", "brand": "Salateira", "city": "Київ"},
    173039: {"name": "Salateira вул.Берковецька", "brand": "Salateira", "city": "Київ"},
    173040: {"name": "Salateira Гната Хоткевича", "brand": "Salateira", "city": "Київ"},
    173043: {"name": "Salateira вулиця Антоновича", "brand": "Salateira", "city": "Київ"},
    173047: {"name": "Salateira Кільцева Дорога", "brand": "Salateira", "city": "Київ"},
    173051: {"name": "Salateira Майдан Незалежності", "brand": "Salateira", "city": "Київ"},
    173052: {"name": "Salateira Михайла Гришка", "brand": "Salateira", "city": "Київ"},
    173058: {"name": "Salateira Спортивна Площа", "brand": "Salateira", "city": "Київ"},
    173069: {"name": "Salateira Проспект Романа Шухевича", "brand": "Salateira", "city": "Київ"},
    173149: {"name": "Salateira вул. Велика Васильківська", "brand": "Salateira", "city": "Київ"},
}

CHORNOMORKA_PROVIDERS = {
    189178: {"name": "Чорноморка Ужгород", "brand": "Чорноморка", "city": "Ужгород"},
    202318: {"name": "Чорноморка на Русанівці", "brand": "Чорноморка", "city": "Київ"},
    202324: {"name": "Чорноморка Преображенська", "brand": "Чорноморка", "city": "Київ"},
    202326: {"name": "Чорноморка Лаврська", "brand": "Чорноморка", "city": "Київ"},
    202331: {"name": "Чорноморка Луцьк", "brand": "Чорноморка", "city": "Луцьк"},
    202333: {"name": "Чорноморка на Петропавлівській Борщагівці", "brand": "Чорноморка", "city": "Київ"},
    202334: {"name": "Чорноморка Ярославська", "brand": "Чорноморка", "city": "Київ"},
    202338: {"name": "Чорноморка Успішна", "brand": "Чорноморка", "city": "Київ"},
    202339: {"name": "Чорноморка Чернівці", "brand": "Чорноморка", "city": "Чернівці"},
    202341: {"name": "Чорноморка Біла Церква", "brand": "Чорноморка", "city": "Біла Церква"},
    202349: {"name": "Чорноморка Велика Васильківська", "brand": "Чорноморка", "city": "Київ"},
    202375: {"name": "Чорноморка Княжий затон", "brand": "Чорноморка", "city": "Київ"},
    202378: {"name": "Чорноморка Івасюка", "brand": "Чорноморка", "city": "Київ"},
    202379: {"name": "Чорноморка Драгоманова", "brand": "Чорноморка", "city": "Київ"},
    202964: {"name": "Чорноморка Вінниця", "brand": "Чорноморка", "city": "Вінниця"},
    203155: {"name": "Чорноморка пр-т Берестейський", "brand": "Чорноморка", "city": "Київ"},
    203170: {"name": "Чорноморка Бровари", "brand": "Чорноморка", "city": "Бровари"},
    203180: {"name": "Чорноморка Черкаси", "brand": "Чорноморка", "city": "Черкаси"},
    203192: {"name": "Чорноморка Буча", "brand": "Чорноморка", "city": "Ірпінь"},
    203194: {"name": "Чорноморка на Печерську", "brand": "Чорноморка", "city": "Київ"},
    203197: {"name": "Чорноморка на Чикаленка", "brand": "Чорноморка", "city": "Київ"},
    832507: {"name": "Чорноморка на Нивках", "brand": "Чорноморка", "city": "Київ"},
    203223: {"name": "Чорноморка в Республіці", "brand": "Чорноморка", "city": "Київ"},
    203228: {"name": "Чорноморка Іллєнка", "brand": "Чорноморка", "city": "Київ"},
    202367: {"name": "Анчоусна від Чорноморки Рівне", "brand": "Анчоусна", "city": "Рівне"},
    203567: {"name": "Анчоусна від Чорноморки Південна", "brand": "Анчоусна", "city": "Дніпро"},
    203578: {"name": "Анчоусна від Чорноморки Барикадна", "brand": "Анчоусна", "city": "Дніпро"},
}

PARTNERS = {
    "salateira": {
        "display_name": "Salateira",
        "emoji": "🥗",
        "brand_color": "#2AAF6D",
        "github_folder": "salateira-weekly",
        "providers": SALATEIRA_PROVIDERS,
    },
    "chornomorka": {
        "display_name": "Чорноморка",
        "emoji": "🐟",
        "brand_color": "#1565C0",
        "github_folder": "chornomorka-weekly",
        "providers": CHORNOMORKA_PROVIDERS,
    },
}

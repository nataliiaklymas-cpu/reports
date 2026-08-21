"""
Registry of partners with active weekly-report automation.

To onboard a new partner: add an entry to PARTNERS with its provider_id -> name/city
mapping and a couple of style params. Optional `locale="en"` switches the weekly
HTML (and index pages) to English; default is Ukrainian.
No other code changes are needed — run_weekly_reports.py loops over this dict.
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

MUZA_PROVIDERS = {
    129340: {"name": "Муза вул. Саксаганського", "brand": "Муза", "city": "Київ"},
    132445: {"name": "Муза вул. Срібнокільська", "brand": "Муза", "city": "Київ"},
    140973: {"name": "Муза вул. Вінстона Черчиля", "brand": "Муза", "city": "Київ"},
    149712: {"name": "Муза вул. Героїв Полку Азов", "brand": "Муза", "city": "Київ"},
    156163: {"name": "Муза вул. Гарматна", "brand": "Муза", "city": "Київ"},
    174670: {"name": "Муза пров. Коломийський", "brand": "Муза", "city": "Київ"},
    190486: {"name": "Муза вул. Лаврухіна", "brand": "Муза", "city": "Київ"},
    192157: {"name": "Муза на Бастіонній", "brand": "Муза", "city": "Київ"},
    192171: {"name": "Муза вул. Пилипа Орлика", "brand": "Муза", "city": "Львів"},
    892705: {"name": "Муза вул. Олександра Олеся", "brand": "Муза", "city": "Київ"},
    169180: {"name": "Муза Пекарська", "brand": "Муза", "city": "Львів"},
    184842: {"name": "Муза Чорновола", "brand": "Муза", "city": "Львів"},
    184854: {"name": "Муза Федьковича", "brand": "Муза", "city": "Львів"},
    200335: {"name": "Муза Рівне", "brand": "Муза", "city": "Рівне"},
    322668: {"name": "Муза пров. Олекси Тихого", "brand": "Муза", "city": "Ірпінь"},
    # Excluded (deleted providers on the platform, confirmed live in Databricks):
    #   177297 Муза пр-т Європейського Союзу — status "deleted"
    #   201208 Муза м. Ірпінь — status "deleted" (replaced by 322668 above)
}

EUROPIANO_PROVIDERS = {
    412639: {"name": "Європіано пров. Коломийський", "brand": "Європіано", "city": "Київ"},
    502633: {"name": "Європіано вул. Вінстона Черчилля", "brand": "Європіано", "city": "Київ"},
    652646: {"name": "Європіано вул. Гарматна", "brand": "Європіано", "city": "Київ"},
    802633: {"name": "Європіано вул. Героїв Полку Азов", "brand": "Європіано", "city": "Київ"},
    982639: {"name": "Європіано вул. Саксаганського", "brand": "Європіано", "city": "Київ"},
    1012643: {"name": "Європіано вул. Бастіонна", "brand": "Європіано", "city": "Київ"},
}

GREEK_HOUSE_PROVIDERS = {
    177104: {"name": "Greek House ТРЦ Sky Mall", "brand": "Greek House", "city": "Київ"},
    177065: {"name": "Greek House ТРК Проспект", "brand": "Greek House", "city": "Київ"},
    177094: {"name": "Greek House ТРЦ Smart Plaza", "brand": "Greek House", "city": "Київ"},
    177056: {"name": "Greek House ТРЦ Respublika Park", "brand": "Greek House", "city": "Київ"},
    177074: {"name": "Greek House ТРЦ Retroville", "brand": "Greek House", "city": "Київ"},
    177069: {"name": "Greek House ТЦ GLOBUS", "brand": "Greek House", "city": "Київ"},
    177071: {"name": "Greek House ТРЦ Piramida", "brand": "Greek House", "city": "Київ"},
    177107: {"name": "Greek House ТРЦ Lavina Mall", "brand": "Greek House", "city": "Київ"},
}

HESBURGER_PROVIDERS = {
    98398: {"name": "Hesburger Vyshneve", "brand": "Hesburger", "city": "Kyiv"},
    98329: {"name": "Hesburger Pavla Polubotka", "brand": "Hesburger", "city": "Kyiv"},
    98397: {"name": "Hesburger Zdolbunivska", "brand": "Hesburger", "city": "Kyiv"},
    98399: {"name": "Hesburger Kyivska", "brand": "Hesburger", "city": "Brovary"},
    98280: {"name": "Hesburger Shevchenka", "brand": "Hesburger", "city": "Irpin"},
    98298: {"name": "Hesburger Kyivskyi Shliakh", "brand": "Hesburger", "city": "Boryspil"},
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
    "muza": {
        "display_name": "Муза",
        "emoji": "🏛️",
        "brand_color": "#FFA500",
        "github_folder": "muza-weekly",
        "providers": MUZA_PROVIDERS,
    },
    "europiano": {
        "display_name": "Європіано by Muza",
        "emoji": "🎹",
        "brand_color": "#7C3AED",
        "github_folder": "europiano-weekly",
        "providers": EUROPIANO_PROVIDERS,
    },
    "greek_house": {
        "display_name": "Greek House",
        "emoji": "🏛️",
        "brand_color": "#0C2C1C",
        "github_folder": "greek-house-weekly",
        "providers": GREEK_HOUSE_PROVIDERS,
    },
    "hesburger": {
        "display_name": "Hesburger",
        "emoji": "🍔",
        "brand_color": "#FFC72C",
        "github_folder": "hesburger-weekly",
        "providers": HESBURGER_PROVIDERS,
        "locale": "en",
    },
}

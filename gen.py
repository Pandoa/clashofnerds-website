import os
import sys
import json
from pathlib import Path

LANGUAGE_TO_GOOGLE_PLAY_BADGE = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "ar-SA": "Arabic-Saudi-Arabia",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "eu": "Basque",
    "be": "Belarusian",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "my": "Burmese",
    "ca": "Catalan",
    "zh-CN": "Chinese-China",
    "zh-TW": "Chinese-Taiwan",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "et": "Estonian",
    "fil": "Filipino",
    "fi": "Finnish",
    "fr-CA": "French-CA",
    "fr": "French",
    "gl": "Galician",
    "ka": "Georgian",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "he": "Hebrew",
    "hi": "Hindi",
    "hu": "Hungarian",
    "is": "Icelandic",
    "id": "Indonesian",
    "ga": "Irish",
    "it": "Italian",
    "kn": "Kannada",
    "kk": "Kazakh",
    "km": "Khmer",
    "ko": "Korean",
    "ky": "Kyrgyz",
    "lo": "Lao",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "ms": "Malaysian",
    "mr": "Marathi",
    "mn": "Mongolian",
    "ne": "Nepali",
    "no": "Norwegian",
    "fa": "Persian",
    "pl": "Polish",
    "pt-BR": "Portuguese-Brazil",
    "pt-PT": "Portuguese-Portugal",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "si": "Sinhalese",
    "sk": "Slovak",
    "sl": "Slovenian",
    "es-419": "Spanish-LATAM",
    "es": "Spanish",
    "sw": "Swahili",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukranian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "zu": "Zulu",
    "bn": "Bengali",
    "ja": "Japanese",
}

flags = {
    "ar": "sa",
    "de": "de",
    "en": "gb",
    "es-ES": "es",
    "es-MX": "mx",
    "fr": "fr",
    "hi": "in",
    "id": "id",
    "it": "it",
    "ja": "jp",
    "ko": "kr",
    "pl": "pl",
    "pt-BR": "br",
    "ru": "ru",
    "th": "th",
    "tr": "tr",
    "vi": "vn",
    "zh-CN": "cn",
}

app_store_locale_map = {
    "ar": "sa",
    "de": "de",
    "en": "us",
    "es-ES": "es",
    "es-MX": "mx",
    "fr": "fr",
    "hi": "in",
    "id": "id",
    "it": "it",
    "ja": "jp",
    "ko": "kr",
    "pl": "pl",
    "pt-BR": "br",
    "ru": "ru",
    "th": "th",
    "tr": "tr",
    "vi": "vn",
    "zh-CN": "cn",
}

template_dir = {
    "index": "",
    "flags": "flags",
}


def main():
    templates = [
        t.removesuffix(".template.html")
        for t in os.listdir("templates")
        if t.endswith(".template.html")
    ]

    pages = 0

    for template in templates:
        language_files = os.listdir(os.path.join("lang", template))

        languages = {}

        for lang in language_files:
            with open(
                os.path.join("lang", template, lang),
                "r",
                encoding="utf-8",
            ) as f:
                languages[Path(lang).stem] = json.load(f)

        languages[""] = languages.pop("en")

        with open(
            f"templates/{template}.template.html",
            "r",
            encoding="utf-8",
        ) as f:
            template_data = f.read()

        lang_pages = "\n".join(
            [
                f'<li class="site-lang"><a href="https://clashofnerds.com/{lang}">'
                f'<img src="https://flagcdn.com/w40/{flags[lang or "en"]}.png" '
                f'alt="flag {lang}">'
                f'{LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang or "en") or LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang.split("-")[0]) or "English"}'
                f"</a></li>"
                for lang in languages.keys()
            ]
        )

        for lang, all_props in languages.items():
            root = os.path.join("docs", lang)
            os.makedirs(root, exist_ok=True)

            pseo_links = "\n".join(
                [
                    f'<li><a href="https://clashofnerds.com/'
                    f'{f"{lang}/" if lang else ""}'
                    f'{props["out_filename"]}" target="_blank" '
                    f'rel="noopener">{props["title"]}</a></li>'
                    for props in all_props
                ]
            )

            lang = lang or "en"

            for props in all_props:
                lang_template = template_data

                output_name = (
                    props["out_filename"].split(".")[0]
                    if props["out_filename"] != "index.html"
                    else ""
                )

                props["canonical"] = (
                    f'<link rel="canonical" '
                    f'href="https://clashofnerds.com/{lang}/{output_name}">'
                    if len(lang) and lang != "en"
                    else f'<link rel="canonical" '
                         f'href="https://clashofnerds.com/{output_name}">'
                )

                props["langcode"] = lang

                props["xlangs"] = "\n".join(
                    [
                        f'<link rel="alternate" hreflang="x-default" '
                        f'href="https://clashofnerds.com/{output_name}">',
                        f'<link rel="alternate" hreflang="en" '
                        f'href="https://clashofnerds.com/{output_name}">',
                        *[
                            f'<link rel="alternate" hreflang="{other_lang}" '
                            f'href="https://clashofnerds.com/{other_lang}/{output_name}">'
                            for other_lang in languages.keys()
                            if other_lang
                        ],
                    ]
                )

                props["pseoSites"] = pseo_links
                props["langSites"] = lang_pages

                props["url"] = (
                    f"https://clashofnerds.com/{lang}/{output_name}"
                    if len(lang) and lang != "en"
                    else f"https://clashofnerds.com/{output_name}"
                )

                props["badge_lang"] = (
                    LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang)
                    or LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(
                        lang.split("-")[0],
                        "English",
                    )
                )

                props["appstore_lang"] = app_store_locale_map[lang]

                for key, value in props.items():
                    lang_template = lang_template.replace(
                        "{{" + key + "}}",
                        value or "",
                    )

                out_dir = f'{root}/{template_dir[template]}'
                os.makedirs(out_dir, exist_ok=True)

                lang_template = lang_template.replace(
                    "https://clashofnerds.com/en/",
                    "https://clashofnerds.com/",
                )

                with open(
                    os.path.join(out_dir, props["out_filename"]),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(lang_template)

                pages += 1

    print("Pages generated:", pages)

    base_url = "https://clashofnerds.com"

    all_translations = []

    for template in templates:
        language_files = os.listdir(os.path.join("lang", template))

        languages = {}

        for lang in language_files:
            with open(
                os.path.join("lang", template, lang),
                "r",
                encoding="utf-8",
            ) as f:
                languages[Path(lang).stem] = json.load(f)

        languages[""] = languages.pop("en")

        translations = {}

        for lang, all_props in languages.items():
            for props in all_props:
                translations.setdefault(
                    props["out_filename"],
                    {},
                )[lang] = props

        all_translations.append(
            (
                template,
                translations,
            )
        )

    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
"""

    for template, translations in all_translations:
        template_prefix = template_dir[template]

        for pages_for_filename in translations.values():
            for lang, props in pages_for_filename.items():
                prefix = f"/{lang}" if lang else ""

                template_prefix_url = (
                    f"/{template_prefix}"
                    if template_prefix
                    else ""
                )

                name = (
                    ""
                    if props["out_filename"] == "index.html"
                    else props["out_filename"].removesuffix(".html")
                )

                # Index pages get a trailing slash.
                # Non-index pages do not.
                url = (
                    f"{base_url}{prefix}{template_prefix_url}/{name}"
                    if name
                    else f"{base_url}{prefix}{template_prefix_url}/"
                )

                sitemap += (
                    "  <url>\n"
                    f"    <loc>{url}</loc>\n"
                )

                for other_lang, other_props in pages_for_filename.items():
                    other_prefix = (
                        f"/{other_lang}"
                        if other_lang
                        else ""
                    )

                    other_name = (
                        ""
                        if other_props["out_filename"] == "index.html"
                        else other_props["out_filename"].removesuffix(".html")
                    )

                    other_url = (
                        f"{base_url}{other_prefix}"
                        f"{template_prefix_url}/{other_name}"
                        if other_name
                        else f"{base_url}{other_prefix}"
                        f"{template_prefix_url}/"
                    )

                    sitemap += (
                        f'    <xhtml:link rel="alternate" '
                        f'hreflang="{other_lang or "en"}" '
                        f'href="{other_url}"/>\n'
                    )

                default_url = (
                    f"{base_url}{template_prefix_url}/{name}"
                    if name
                    else f"{base_url}{template_prefix_url}/"
                )

                sitemap += (
                    '    <xhtml:link rel="alternate" '
                    f'hreflang="x-default" '
                    f'href="{default_url}"/>\n'
                )

                sitemap += "  </url>\n"

    sitemap += "</urlset>\n"

    with open("docs/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)


if __name__ == "__main__":
    main()
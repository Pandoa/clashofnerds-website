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


def main():
    language_files = os.listdir("lang")

    languages = {}
    for lang in language_files:
        with open(os.path.join("lang", lang), "r", encoding="utf-8") as f:
            languages[Path(lang).stem] = json.load(f)

    languages[""] = languages.pop("en")

    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    xlangs = "\n".join(
        [
            f'<link rel="alternate" hreflang="{lang}" href="https://clashofnerds.com/{lang}/">'
            for lang in languages.keys()
            if lang
        ]
    )
    xlangs += '\n<link rel="alternate" hreflang="en" href="https://clashofnerds.com/">'

    lang_pages = "\n".join(
        [
            f'<li class="site-lang"><a href="https://clashofnerds.com/{lang}"><img src="https://flagcdn.com/w40/{flags[lang or 'en']}.png" alt="flag {lang}">{LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang or 'en') or LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang.split('-')[0]) or 'English'}</a></li>'
            for lang in languages.keys()
        ]
    )

    pages = 0
    for lang, all_props in languages.items():
        root = os.path.join("docs", lang)
        os.makedirs(root, exist_ok=True)

        pseo_links = "\n".join(
            [
                f'<li><a href="https://clashofnerds.com/{f"{lang}/" if lang else ""}{props["out_filename"]}" target="_blank" rel="noopener">{props["title"]}</a></li>'
                for props in all_props
            ]
        )

        lang = lang or "en"

        for props in all_props:
            lang_template = template
            output_name = props["out_filename"].split(".")[0] if props["out_filename"] != "index.html" else ""
            props["canonical"] = f'<link rel="canonical" href="https://clashofnerds.com/{output_name}">'
            props["langcode"] = lang
            props["xlangs"] = xlangs
            props["pseoSites"] = pseo_links
            props["langSites"] = lang_pages
            props["badge_lang"] = LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(
                lang
            ) or LANGUAGE_TO_GOOGLE_PLAY_BADGE.get(lang.split("-")[0], "English")

            for key, value in props.items():
                lang_template = lang_template.replace("{{" + key + "}}", value)

            with open(
                os.path.join(root, props["out_filename"]), "w", encoding="utf-8"
            ) as f:
                f.write(lang_template)

            pages += 1

    print("Pages generated:", pages)

    base_url = "https://clashofnerds.com"

    # filename -> language -> props
    translations = {}

    for lang, all_props in languages.items():
        for props in all_props:
            translations.setdefault(props["out_filename"], {})[lang] = props

    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:xhtml="http://www.w3.org/1999/xhtml">
    """

    for pages in translations.values():
        for lang, props in pages.items():
            prefix = f"/{lang}" if lang else ""
            url = f"{base_url}{prefix}/{props['out_filename']}"

            sitemap += f"  <url>\n"
            sitemap += f"    <loc>{url}</loc>\n"

            for other_lang, other_props in pages.items():
                other_prefix = f"/{other_lang}" if other_lang else ""
                other_url = f"{base_url}{other_prefix}/{other_props['out_filename']}"

                sitemap += (
                    f'    <xhtml:link rel="alternate" '
                    f'hreflang="{other_lang or "en"}" '
                    f'href="{other_url}"/>\n'
                )

            sitemap += "  </url>\n"

    sitemap += "</urlset>\n"

    with open("docs/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)


if __name__ == "__main__":
    main()

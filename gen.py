import os
import sys
import json
from pathlib import Path


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
            f'<link rel="alternate" hreflang="{lang}" href="https://pandoa.github.io/clashofnerds-website/{lang}/">'
            for lang in languages.keys()
            if lang
        ]
    )
    xlangs += '<link rel="alternate" hreflang="en" href="https://pandoa.github.io/clashofnerds-website/">'

    pages = 0
    for lang, all_props in languages.items():
        root = os.path.join("docs", lang)
        os.makedirs(root, exist_ok=True)

        pseo_links = "\n".join(
            [
                f'<li><a href="https://pandoa.github.io/clashofnerds-website/{lang}/{props["out_filename"]}" target="_blank" rel="noopener">{props["title"]}</a></li>'
                for props in all_props
            ]
        )

        for props in all_props:
            lang_template = template
            props["langcode"] = lang
            props["xlangs"] = xlangs
            props["pseoSites"] = pseo_links

            for key, value in props.items():
                lang_template = lang_template.replace("{{" + key + "}}", value)

            with open(
                os.path.join(root, props["out_filename"]), "w", encoding="utf-8"
            ) as f:
                f.write(lang_template)

            pages += 1

    print("Pages generated:", pages)

    base_url = "https://pandoa.github.io/clashofnerds-website"

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

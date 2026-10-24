"""Apply the premium editorial design system to the report definition."""
import glob
import json
import os

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(TOOLS_DIR, "..", "olist-analysis.Report", "definition", "pages")
PAGE1 = "41e4ccf47a67dba14efd"
PAGE2 = "7c3f9a2b14d84e6f0a51"
PAGE3 = "b8e2d4c6a1f35b790c42"
SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "visualContainer/2.12.0/schema.json"
)

CANVAS = "#F7F8FA"
WHITE = "#FFFFFF"
INK = "#172B4D"
MUTED = "#667085"
BORDER = "#E5E9EF"
TEAL = "#168C87"
SLATE = "#6686A8"
PALE = "#E8F5F3"
PALE_BORDER = "#CFE4E0"
GRID = "#EDF1F5"

OLD_COLORS = {
    "#0F172A": INK,
    "#334155": INK,
    "#475569": INK,
    "#64748B": MUTED,
    "#94A3B8": SLATE,
    "#2563EB": TEAL,
    "#E2E8F0": BORDER,
    "#EEF2F7": GRID,
    "#10B981": "#39856B",
    "#EF4444": "#C65D5D",
}


# ---------------------------------------------------------------- expressions
def lit(value):
    return {"expr": {"Literal": {"Value": value}}}


def pbool(value):
    return lit("true" if value else "false")


def pnum(value, suffix="D"):
    return lit(f"{value}{suffix}")


def pstr(value):
    return lit("'" + str(value).replace("'", "''") + "'")


def solid(color):
    return {"solid": {"color": pstr(color)}}


def container(
    title=None,
    subtitle=None,
    title_size=12.5,
    title_color=INK,
    title_family="Segoe UI Semibold",
    subtitle_size=9.5,
    background=None,
    border=None,
    padding=None,
    radius=6,
    title_show=None,
):
    vco = {}
    if title is not None or title_show is not None:
        props = {
            "show": pbool(title is not None if title_show is None else title_show),
            "fontSize": pnum(title_size),
            "fontColor": solid(title_color),
            "fontFamily": pstr(title_family),
            "alignment": pstr("left"),
            "titleWrap": pbool(False),
        }
        if title is not None:
            props["text"] = pstr(title)
        vco["title"] = [{"properties": props}]
    if subtitle:
        vco["subTitle"] = [
            {
                "properties": {
                    "show": pbool(True),
                    "text": pstr(subtitle),
                    "fontSize": pnum(subtitle_size),
                    "fontColor": solid(MUTED),
                    "fontFamily": pstr("Segoe UI"),
                    "alignment": pstr("left"),
                }
            }
        ]
    if background:
        vco["background"] = [
            {"properties": {"show": pbool(True), "color": solid(background), "transparency": pnum(0)}}
        ]
    if border:
        vco["border"] = [
            {
                "properties": {
                    "show": pbool(True),
                    "color": solid(border),
                    "radius": pnum(radius),
                    "width": pnum(1),
                }
            }
        ]
    if padding:
        left, top, right, bottom = padding
        vco["padding"] = [
            {
                "properties": {
                    "left": pnum(left),
                    "top": pnum(top),
                    "right": pnum(right),
                    "bottom": pnum(bottom),
                }
            }
        ]
    vco["dropShadow"] = [{"properties": {"show": pbool(False)}}]
    vco["divider"] = [{"properties": {"show": pbool(False)}}]
    vco["visualHeader"] = [{"properties": {"show": pbool(False)}}]
    return vco


# ---------------------------------------------------------------- file access
def vpath(page, name):
    return os.path.join(PAGES, page, "visuals", name, "visual.json")


def load(page, name):
    with open(vpath(page, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(page, name, data):
    path = vpath(page, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def set_position(data, x, y, width, height, z=1):
    data["position"] = {"x": x, "y": y, "z": z, "height": height, "width": width}


def set_title(data, title, subtitle=None):
    data["visual"]["visualContainerObjects"] = container(title, subtitle)


# ---------------------------------------------------------------- query parts
def measure(entity, prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def column(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def projection(field, ref, native=None, active=False):
    item = {"field": field, "queryRef": ref, "nativeQueryRef": native or ref.split(".")[-1]}
    if active:
        item["active"] = True
    return item


def descending(entity, prop):
    return {
        "sort": [{"field": measure(entity, prop), "direction": "Descending"}],
        "isDefaultSort": True,
    }


def theme_colors(node):
    if isinstance(node, dict):
        return {k: theme_colors(v) for k, v in node.items()}
    if isinstance(node, list):
        return [theme_colors(v) for v in node]
    if isinstance(node, str) and node in OLD_COLORS:
        return OLD_COLORS[node]
    return node


# ---------------------------------------------------------------- chart styling
def axis(vis, key, size=9.5, grid=False, color=MUTED):
    props = vis.setdefault("objects", {}).setdefault(key, [{"properties": {}}])
    entry = props[0].setdefault("properties", {})
    entry["show"] = pbool(True)
    entry["showAxisTitle"] = pbool(False)
    entry["labelFontSize"] = pnum(size)
    entry["labelColor"] = solid(color)
    if key == "valueAxis":
        entry["gridlineShow"] = pbool(grid)
        entry["gridlineColor"] = solid(GRID)
        entry["gridlineThickness"] = pnum(1)
    else:
        entry["gridlineShow"] = pbool(False)


def chart(vis, primary=TEAL, labels=False, label_size=9.5, precision=1, legend=False):
    objects = vis.setdefault("objects", {})
    objects["legend"] = [{"properties": {"show": pbool(legend)}}]
    objects["labels"] = [
        {
            "properties": {
                "show": pbool(labels),
                "fontSize": pnum(label_size),
                "color": solid(INK),
                "labelPrecision": pnum(precision, "L"),
            }
        }
    ]
    axis(vis, "categoryAxis")
    axis(vis, "valueAxis", size=9, grid=True)
    objects["dataPoint"] = [{"properties": {"fill": solid(primary)}}]


def line_chart(vis):
    chart(vis, labels=False)
    vis["objects"]["lineStyles"] = [
        {
            "properties": {
                "strokeWidth": pnum(2.5),
                "showMarker": pbool(False),
                "interpolationSmooth": pstr("monotoneX"),
            }
        }
    ]


def donut_chart(vis):
    objects = vis.setdefault("objects", {})
    objects["labels"] = [
        {
            "properties": {
                "show": pbool(True),
                "labelStyle": pstr("Percent of total"),
                "percentageLabelPrecision": pnum(1, "L"),
                "position": pstr("outside"),
                "fontSize": pnum(9.5),
                "color": solid(MUTED),
            }
        }
    ]
    objects["legend"] = [
        {
            "properties": {
                "show": pbool(True),
                "position": pstr("Right"),
                "showTitle": pbool(False),
                "fontSize": pnum(10),
                "labelColor": solid(INK),
            }
        }
    ]
    objects["slices"] = [{"properties": {"innerRadiusRatio": pnum(62, "L")}}]


def set_column_widths(vis, widths):
    vis.setdefault("objects", {})["columnWidth"] = [
        {"properties": {"value": pnum(width, "D")}, "selector": {"metadata": field}}
        for field, width in widths
    ]


def card(page, name, x, y, width, height, title, subtitle, entity, measure_name, value_size=30):
    """Reusable KPI card bound to a single measure."""
    d = load(page, name)
    set_position(d, x, y, width, height)
    vco = container(title, subtitle, title_size=11, title_color=MUTED, title_family="Segoe UI")
    vco["padding"] = [
        {"properties": {"left": pnum(20), "top": pnum(14), "right": pnum(20), "bottom": pnum(12)}}
    ]
    d["visual"]["visualContainerObjects"] = vco
    d["visual"]["objects"] = {
        "label": [
            {
                "properties": {
                    "show": pbool(True),
                    "fontSize": pnum(value_size),
                    "fontColor": solid(INK),
                    "fontFamily": pstr("Segoe UI Semibold"),
                },
                "selector": {"id": "default"},
            }
        ]
    }
    d["visual"]["query"] = {
        "queryState": {
            "Data": {
                "projections": [
                    projection(
                        measure(entity, measure_name),
                        f"{entity}.{measure_name}",
                        measure_name,
                    )
                ]
            }
        },
        "sortDefinition": descending(entity, measure_name),
    }
    save(page, name, d)
    return d


# ---------------------------------------------------------------- textbox
def textbox(page, name, x, y, width, height, paragraphs, vco, z=100):
    data = {"$schema": SCHEMA, "name": name, "position": {}, "visual": {}}
    set_position(data, x, y, width, height, z)
    data["visual"] = {
        "visualType": "textbox",
        "objects": {
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": text,
                                        "textStyle": {
                                            "fontFamily": family,
                                            "fontSize": f"{size}pt",
                                            **({"fontWeight": str(weight)} if weight else {}),
                                            "color": color,
                                        },
                                    }
                                    for text, size, color, weight, family in (
                                        paragraph
                                        or [(" ", 6, INK, None, "Segoe UI")]
                                    )
                                ]
                            }
                            for paragraph in paragraphs
                        ]
                    }
                }
            ]
        },
        "visualContainerObjects": vco,
    }
    save(page, name, data)


def clear_paragraphs(textbox_data):
    textbox_data["visual"]["objects"]["general"][0]["properties"]["paragraphs"] = []


# ---------------------------------------------------------------- header
def header(page, prefix, title, subtitle, width=900):
    textbox(
        page,
        f"{prefix}_brand",
        32,
        6,
        700,
        34,
        [[("OLIST / COMMERCE INTELLIGENCE", 9, TEAL, 600, "Segoe UI Semibold")]],
        container(title_show=False),
        z=1000,
    )
    textbox(
        page,
        f"{prefix}_page_title",
        32,
        42,
        width,
        60,
        [[(title, 28, INK, 600, "Segoe UI Semibold")]],
        container(title_show=False),
        z=1000,
    )
    textbox(
        page,
        f"{prefix}_page_subtitle",
        32,
        104,
        width,
        36,
        [[(subtitle, 12, MUTED, None, "Segoe UI")]],
        container(title_show=False),
        z=1000,
    )


# ---------------------------------------------------------------- page 1
def page_one():
    header(
        PAGE1,
        "overview",
        "Executive Overview",
        "Sales performance, geographic distribution, and marketplace activity.",
    )

    card(PAGE1, "91b7d978055b1459ee3a", 32, 160, 452, 140, "Total sales",
         "Gross merchandise value", "order_items_clean", "Total Sales")
    card(PAGE1, "1f99a39b1d0218baf3fd", 500, 160, 452, 140, "Total orders",
         "Distinct orders placed", "order_items_clean", "Total Orders")
    card(PAGE1, "a89caf417847b8642d28", 968, 160, 452, 140, "Average order value",
         "Sales per order", "order_items_clean", "Avg Order Value")
    card(PAGE1, "fa9175ef5352f155a083", 1436, 160, 452, 140, "Total freight",
         "Freight collected", "order_items_clean", "Total Freight")

    # monthly trend
    d = load(PAGE1, "sales_trend_line")
    set_position(d, 32, 316, 1232, 330)
    set_title(d, "Monthly sales performance", "Gross merchandise value by month")
    line_chart(d["visual"])
    save(PAGE1, "sales_trend_line", d)

    # sales by customer state
    d = load(PAGE1, "sales_by_state")
    set_position(d, 1280, 316, 608, 330)
    set_title(d, "Sales contribution by state", "Top 10 customer states by sales")
    vis = d["visual"]
    category = vis["query"]["queryState"]["Category"]["projections"][0]
    category["field"] = column("customers_clean", "customer_state")
    category["queryRef"] = "customers_clean.customer_state"
    category["nativeQueryRef"] = "customer_state"
    filter_entry = d["filterConfig"]["filters"][0]
    filter_entry["field"] = column("customers_clean", "customer_state")
    filter_entry["filter"]["From"][0]["Entity"] = "customers_clean"
    vis["query"]["sortDefinition"] = descending("order_items_clean", "Total Sales")
    vis["objects"] = {}
    chart(vis, labels=False)
    save(PAGE1, "sales_by_state", d)

    # top categories
    d = load(PAGE1, "top_5_categories")
    set_position(d, 32, 662, 608, 386)
    set_title(d, "Top product categories", "Five highest-selling categories")
    d["visual"]["objects"] = {}
    chart(d["visual"], labels=False)
    save(PAGE1, "top_5_categories", d)

    # payment mix
    d = load(PAGE1, "payment_donut")
    set_position(d, 656, 662, 608, 386)
    set_title(d, "Payment methods", "Share of total payment value")
    donut_chart(d["visual"])
    save(PAGE1, "payment_donut", d)

    # top sellers table
    d = load(PAGE1, "top_sellers")
    set_position(d, 1280, 662, 608, 386)
    set_title(d, "Top sellers", "Right-click a seller to drill through")
    vis = d["visual"]
    projections = vis["query"]["queryState"]["Values"]["projections"]
    by_ref = {item["queryRef"]: item for item in projections}
    vis["query"]["queryState"]["Values"]["projections"] = [
        by_ref[ref]
        for ref in (
            "sellers_clean.seller_id",
            "sellers_clean.seller_city",
            "order_items_clean.Total Sales",
        )
        if ref in by_ref
    ]
    set_column_widths(
        vis,
        [
            ("sellers_clean.seller_id", 230),
            ("sellers_clean.seller_city", 170),
            ("order_items_clean.Total Sales", 208),
        ],
    )
    save(PAGE1, "top_sellers", d)

    # filters
    for name, x, width, title in [
        ("slicer_date", 1024, 296, "Date range"),
        ("slicer_state", 1332, 260, "Customer state"),
        ("slicer_status", 1604, 284, "Order status"),
    ]:
        d = load(PAGE1, name)
        set_position(d, x, 44, width, 94)
        vco = container(title, None, title_size=9.5, title_color=MUTED, title_family="Segoe UI")
        vco["padding"] = [
            {"properties": {"left": pnum(14), "top": pnum(8), "right": pnum(14), "bottom": pnum(6)}}
        ]
        d["visual"]["visualContainerObjects"] = vco
        save(PAGE1, name, d)

    divider(PAGE1, "overview_divider", 32, 146, 1856)


# ---------------------------------------------------------------- page 2
INSIGHT_BODY = [
    [
        (
            "Late-delivered orders averaged 2.27 review stars, compared with 4.29 for "
            "on-time orders — a gap of 2.02 stars across 96,359 delivered orders.",
            13,
            INK,
            600,
            "Segoe UI Semibold",
        )
    ],
    [
        (
            "Welch’s t-test confirms the difference is statistically significant "
            "(t = −100.97, p < 0.001), and the standardized effect size is large "
            "(Cohen’s d = −1.47). The gap is meaningful in magnitude, not only in "
            "statistical confidence.",
            10.5,
            MUTED,
            None,
            "Segoe UI",
        )
    ],
    [
        (
            "The analysis is observational: it establishes a strong association "
            "between delivery delays and lower satisfaction, not causation. Delivery "
            "reliability should be treated as a leading indicator of customer "
            "experience rather than a proven cause.",
            10.5,
            MUTED,
            None,
            "Segoe UI",
        )
    ],
]


def in_filter(name, entity, prop, values):
    return {
        "filters": [
            {
                "name": name,
                "field": column(entity, prop),
                "type": "Categorical",
                "filter": {
                    "Version": 2,
                    "From": [{"Name": "o", "Entity": entity, "Type": 0}],
                    "Where": [
                        {
                            "Condition": {
                                "In": {
                                    "Expressions": [
                                        {
                                            "Column": {
                                                "Expression": {"SourceRef": {"Source": "o"}},
                                                "Property": prop,
                                            }
                                        }
                                    ],
                                    "Values": [
                                        [{"Literal": {"Value": pstr(value)["expr"]["Literal"]["Value"]}}]
                                        for value in values
                                    ],
                                }
                            }
                        }
                    ],
                },
            }
        ]
    }


def evidence_chart():
    data = {"$schema": SCHEMA, "name": "evidence_chart", "position": {}, "visual": {}}
    set_position(data, 1168, 684, 720, 364)
    data["visual"] = {
        "visualType": "barChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [
                        projection(
                            column("orders_clean", "Delivery Status"),
                            "orders_clean.Delivery Status",
                            "Delivery Status",
                            True,
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        projection(
                            measure("order_reviews_clean", "Avg Review Score"),
                            "order_reviews_clean.Avg Review Score",
                            "Avg Review Score",
                        )
                    ]
                },
            },
            "sortDefinition": descending("order_reviews_clean", "Avg Review Score"),
        },
        "objects": {},
        "visualContainerObjects": container(
            "Late deliveries and review scores",
            "Average stars · t = −100.97 · p < 0.001 · Cohen’s d = −1.47",
        ),
    }
    chart(data["visual"], labels=True, label_size=11, precision=2)
    data["filterConfig"] = in_filter(
        "delivery_groups", "orders_clean", "Delivery Status", ["On time", "Late delivery"]
    )
    save(PAGE2, "evidence_chart", data)


def page_two():
    header(
        PAGE2,
        "review",
        "Delivery & Customer Experience",
        "Understanding delivery performance and customer satisfaction.",
        width=1100,
    )

    card(PAGE2, "card_avg_review", 32, 160, 452, 140, "Average review score",
         "Out of 5 stars", "order_reviews_clean", "Avg Review Score")
    card(PAGE2, "card_late_rate", 500, 160, 452, 140, "Late delivery rate",
         "Share of delivered orders", "orders_clean", "Late Delivery %")
    card(PAGE2, "card_total_reviews", 968, 160, 452, 140, "Total reviews",
         "Customer reviews received", "order_reviews_clean", "Total Reviews")
    card(PAGE2, "card_on_time", 1436, 160, 452, 140, "On-time delivery rate",
         "Delivered by estimate", "orders_clean", "On-Time Delivery %")

    d = load(PAGE2, "review_by_delay")
    set_position(d, 32, 316, 760, 352)
    set_title(
        d,
        "Average review score by delivery delay",
        "Scores 1–5, grouped by days early or late",
    )
    chart(d["visual"], labels=True, label_size=10, precision=2)
    save(PAGE2, "review_by_delay", d)

    d = load(PAGE2, "review_distribution")
    set_position(d, 808, 316, 1080, 352)
    set_title(d, "Review score distribution", "Number of reviews by score, 1 to 5")
    chart(d["visual"], primary=SLATE, labels=True, label_size=10, precision=0)
    save(PAGE2, "review_distribution", d)

    textbox(
        PAGE2,
        "insight_panel",
        32,
        684,
        1120,
        364,
        INSIGHT_BODY,
        container(
            "Delivery performance and customer satisfaction",
            None,
            title_size=15,
            background=WHITE,
            border=BORDER,
            padding=(28, 22, 28, 22),
        ),
        z=100,
    )

    evidence_chart()

    divider(PAGE2, "review_divider", 32, 146, 1856)


# ---------------------------------------------------------------- page 3
def page_three():
    header(
        PAGE3,
        "seller",
        "Seller Intelligence",
        "Sales performance and product-category contribution for the selected seller.",
        width=1000,
    )

    save(PAGE3, "selected_seller_card",
         card(PAGE3, "selected_seller_card", 1128, 34, 520, 88,
              "Selected seller", None, "sellers_clean", "Selected Seller", value_size=13))

    button(PAGE3, "btn_back_overview", 1684, 36, 204, 36, "←  Back to overview",
           fill=WHITE, text=INK, line=BORDER, link_type="Back", target=None)

    card(PAGE3, "card_sales", 32, 160, 452, 140, "Total sales", None,
         "order_items_clean", "Total Sales")
    card(PAGE3, "card_orders", 500, 160, 452, 140, "Total orders", None,
         "order_items_clean", "Total Orders")
    card(PAGE3, "card_aov", 968, 160, 452, 140, "Average order value", None,
         "order_items_clean", "Avg Order Value")
    card(PAGE3, "card_freight", 1436, 160, 452, 140, "Total freight", None,
         "order_items_clean", "Total Freight")

    button(PAGE3, "btn_category_view", 32, 316, 232, 40, "Category performance",
           fill=TEAL, text=WHITE, line=TEAL, link_type="Bookmark",
           target="3d9f1a6c2b8e4075a1f3")
    button(PAGE3, "btn_order_details", 276, 316, 176, 40, "Order details",
           fill=WHITE, text=INK, line=BORDER, link_type="Bookmark",
           target="c47e2b9d8a1f6053e7b2")

    d = load(PAGE3, "seller_category_chart")
    set_position(d, 32, 372, 1856, 676, z=2)
    set_title(d, "Category performance",
              "Sales by product category for the selected seller")
    d["filterConfig"] = top_n_filter(
        "top10_seller_categories",
        "products_clean",
        "product_category_name_english",
        10,
    )
    d["visual"]["objects"] = {}
    chart(d["visual"], labels=False)
    save(PAGE3, "seller_category_chart", d)

    d = load(PAGE3, "seller_items_table")
    set_position(d, 32, 372, 1856, 676, z=1)
    set_title(d, "Order details",
              "Order items for the selected seller, most recent first")
    set_column_widths(
        d["visual"],
        [
            ("order_items_clean.order_id", 250),
            ("orders_clean.order_purchase_timestamp", 220),
            ("products_clean.product_category_name_english", 700),
            ("order_items_clean.price", 200),
            ("order_items_clean.freight_value", 200),
            ("orders_clean.order_status", 180),
        ],
    )
    save(PAGE3, "seller_items_table", d)

    divider(PAGE3, "seller_divider", 32, 146, 1856)


# ---------------------------------------------------------------- primitives
def divider(page, name, x, y, width):
    data = {"$schema": SCHEMA, "name": name, "position": {}, "visual": {}}
    set_position(data, x, y, width, 1, z=0)
    data["visual"] = {
        "visualType": "shape",
        "objects": {
            "shape": [{"properties": {"tileShape": pstr("rectangle")}}],
            "fill": [{"properties": {"show": pbool(True), "fillColor": solid(BORDER)}}],
            "outline": [{"properties": {"show": pbool(False)}}],
            "rotation": [{"properties": {"shapeAngle": pnum(0, "L")}}],
        },
        "visualContainerObjects": {
            "title": [{"properties": {"show": pbool(False)}}],
            "background": [{"properties": {"show": pbool(False)}}],
            "border": [{"properties": {"show": pbool(False)}}],
            "dropShadow": [{"properties": {"show": pbool(False)}}],
            "visualHeader": [{"properties": {"show": pbool(False)}}],
        },
    }
    save(page, name, data)


def button(page, name, x, y, width, height, label, fill, text, line, link_type, target):
    data = {"$schema": SCHEMA, "name": name, "position": {}, "visual": {}}
    set_position(data, x, y, width, height, z=3)
    link = {"show": pbool(True), "type": pstr(link_type)}
    if link_type == "PageNavigation":
        link["navigationSection"] = pstr(target)
    elif link_type == "Bookmark":
        link["bookmark"] = pstr(target)
    data["visual"] = {
        "visualType": "actionButton",
        "objects": {
            "text": [
                {
                    "properties": {
                        "show": pbool(True),
                        "text": pstr(label),
                        "fontColor": solid(text),
                        "fontSize": pnum(10.5),
                        "fontFamily": pstr("Segoe UI Semibold"),
                        "horizontalAlignment": pstr("center"),
                        "verticalAlignment": pstr("center"),
                    },
                    "selector": {"id": "default"},
                }
            ],
            "fill": [
                {
                    "properties": {"show": pbool(True), "fillColor": solid(fill)},
                    "selector": {"id": "default"},
                }
            ],
            "outline": [
                {
                    "properties": {
                        "show": pbool(True),
                        "lineColor": solid(line),
                        "weight": pnum(1),
                        "radius": pnum(6),
                    },
                    "selector": {"id": "default"},
                }
            ],
        },
        "visualContainerObjects": {
            "visualLink": [{"properties": link}],
            "title": [{"properties": {"show": pbool(False)}}],
            "background": [{"properties": {"show": pbool(False)}}],
            "border": [{"properties": {"show": pbool(False)}}],
            "dropShadow": [{"properties": {"show": pbool(False)}}],
            "visualHeader": [{"properties": {"show": pbool(False)}}],
        },
    }
    save(page, name, data)


def top_n_filter(name, entity, prop, count):
    return {
        "filters": [
            {
                "name": name,
                "field": column(entity, prop),
                "type": "TopN",
                "filter": {
                    "Version": 2,
                    "From": [{"Name": "s", "Entity": entity, "Type": 0}],
                    "Where": [{"Condition": {"VisualTopN": {"ItemCount": count}}}],
                },
            }
        ]
    }


# ---------------------------------------------------------------- theme
def theme():
    palette = [TEAL, SLATE, "#8FB3AE", "#A9BFD6", "#C9B9A8", "#7F9C94", "#D6C2A8", "#5C7A8A"]
    off_container = {
        "background": [{"show": False}],
        "border": [{"show": False}],
        "dropShadow": [{"show": False}],
        "title": [{"show": False}],
        "visualHeader": [{"show": False}],
    }
    data = {
        "name": "Olist_Clean3552439278458003",
        "dataColors": palette,
        "background": WHITE,
        "foreground": INK,
        "tableAccent": TEAL,
        "good": "#39856B",
        "neutral": "#B08A3E",
        "bad": "#C65D5D",
        "maximum": TEAL,
        "center": BORDER,
        "minimum": PALE,
        "textClasses": {
            "callout": {"fontSize": 30, "fontFace": "Segoe UI Semibold", "color": INK},
            "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": INK},
            "header": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": INK},
            "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": MUTED},
        },
        "visualStyles": {
            "page": {
                "*": {
                    "background": [
                        {"transparency": 0, "color": {"solid": {"color": CANVAS}}}
                    ]
                }
            },
            "*": {
                "*": {
                    "background": [
                        {"show": True, "transparency": 0, "color": {"solid": {"color": WHITE}}}
                    ],
                    "border": [
                        {"show": True, "color": {"solid": {"color": BORDER}}, "radius": 6}
                    ],
                    "dropShadow": [{"show": False}],
                    "divider": [{"show": False}],
                    "visualHeader": [{"show": False}],
                    "title": [
                        {
                            "show": True,
                            "fontColor": {"solid": {"color": INK}},
                            "fontSize": 12.5,
                            "fontFamily": "Segoe UI Semibold",
                            "alignment": "left",
                        }
                    ],
                    "subTitle": [
                        {
                            "show": True,
                            "fontColor": {"solid": {"color": MUTED}},
                            "fontSize": 9.5,
                            "fontFamily": "Segoe UI",
                            "alignment": "left",
                        }
                    ],
                }
            },
            "textbox": {"*": off_container},
            "shape": {"*": off_container},
            "actionButton": {
                "*": {
                    **off_container,
                    "outline": [
                        {
                            "show": True,
                            "lineColor": {"solid": {"color": BORDER}},
                            "weight": 1,
                        }
                    ],
                    "fill": [{"show": True, "fillColor": {"solid": {"color": WHITE}}}],
                    "text": [
                        {
                            "fontColor": {"solid": {"color": INK}},
                            "fontSize": 10.5,
                            "fontFamily": "Segoe UI Semibold",
                        }
                    ],
                }
            },
            "cardVisual": {
                "*": {
                    "label": [
                        {
                            "show": True,
                            "fontSize": 30,
                            "fontColor": {"solid": {"color": INK}},
                            "fontFamily": "Segoe UI Semibold",
                        }
                    ]
                }
            },
            "card": {
                "*": {
                    "labels": [
                        {"fontSize": 30, "color": {"solid": {"color": INK}}}
                    ],
                    "categoryLabels": [
                        {"fontSize": 10.5, "color": {"solid": {"color": MUTED}}}
                    ],
                }
            },
            "lineChart": {
                "*": {
                    "lineStyles": [
                        {
                            "strokeWidth": 2.5,
                            "showMarker": False,
                            "interpolationSmooth": "monotoneX",
                        }
                    ],
                    "dataPoint": [{"fill": {"solid": {"color": TEAL}}}],
                }
            },
            "barChart": {
                "*": {
                    "dataPoint": [{"fill": {"solid": {"color": TEAL}}}],
                    "labels": [{"fontSize": 9.5, "color": {"solid": {"color": INK}}}],
                    "legend": [{"show": False}],
                }
            },
            "columnChart": {
                "*": {
                    "dataPoint": [{"fill": {"solid": {"color": TEAL}}}],
                    "labels": [{"fontSize": 9.5, "color": {"solid": {"color": INK}}}],
                    "legend": [{"show": False}],
                }
            },
            "donutChart": {
                "*": {
                    "slices": [{"innerRadiusRatio": 62}],
                    "legend": [
                        {
                            "show": True,
                            "position": "Right",
                            "showTitle": False,
                            "fontSize": 10,
                            "labelColor": {"solid": {"color": INK}},
                        }
                    ],
                    "labels": [
                        {
                            "show": True,
                            "labelStyle": "Percent of total",
                            "position": "outside",
                            "fontSize": 9.5,
                            "color": {"solid": {"color": MUTED}},
                        }
                    ],
                }
            },
            "tableEx": {
                "*": {
                    "grid": [
                        {
                            "gridHorizontal": True,
                            "gridHorizontalColor": {"solid": {"color": GRID}},
                            "outlineStyle": 0,
                            "rowPadding": 8,
                        }
                    ],
                    "columnHeaders": [
                        {
                            "fontColor": {"solid": {"color": MUTED}},
                            "backColor": {"solid": {"color": CANVAS}},
                            "bold": True,
                            "fontSize": 9.5,
                        }
                    ],
                    "values": [
                        {"fontColor": {"solid": {"color": INK}}, "fontSize": 10}
                    ],
                }
            },
            "slicer": {
                "*": {
                    "header": [{"show": False}],
                    "data": [{"mode": "Dropdown"}],
                    "items": [
                        {"fontColor": {"solid": {"color": INK}}, "textSize": 10}
                    ],
                }
            },
        },
    }
    text = json.dumps(data, indent=2) + "\n"
    with open("Theme/olist_theme.json", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(
        "olist-analysis.Report/StaticResources/RegisteredResources/"
        "Olist_Clean3552439278458003.json",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as fh:
        fh.write(text)


# ---------------------------------------------------------------- bookmarks
def bookmarks():
    def visual_container(hidden=False, merges=None):
        payload = {}
        if hidden:
            payload["display"] = {"mode": "hidden"}
        if merges:
            payload["objects"] = {"merge": merges}
        return {"singleVisual": payload}

    fill_merge = lambda color: {"fill": [{"properties": {"fillColor": solid(color)}}]}
    text_merge = lambda color: {"text": [{"properties": {"fontColor": solid(color)}}]}
    line_merge = lambda color: {"outline": [{"properties": {"lineColor": solid(color)}}]}

    def make(hidden_visual):
        category_active = hidden_visual == "seller_items_table"
        return {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/"
            "definition/bookmark/1.4.0/schema.json",
            "displayName": "Category performance" if category_active else "Order details",
            "name": "3d9f1a6c2b8e4075a1f3"
            if category_active
            else "c47e2b9d8a1f6053e7b2",
            "options": {
                "applyOnlyToTargetVisuals": True,
                "targetVisualNames": [
                    "seller_category_chart",
                    "seller_items_table",
                    "btn_category_view",
                    "btn_order_details",
                ],
                "suppressData": True,
                "suppressActiveSection": True,
            },
            "explorationState": {
                "version": "1.3",
                "activeSection": PAGE3,
                "sections": {
                    PAGE3: {
                        "visualContainers": {
                            "seller_category_chart": visual_container(
                                hidden=hidden_visual == "seller_category_chart"
                            ),
                            "seller_items_table": visual_container(
                                hidden=hidden_visual == "seller_items_table"
                            ),
                            "btn_category_view": visual_container(
                                merges={
                                    **fill_merge(TEAL if category_active else WHITE),
                                    **text_merge(WHITE if category_active else INK),
                                    **line_merge(TEAL if category_active else BORDER),
                                }
                            ),
                            "btn_order_details": visual_container(
                                merges={
                                    **fill_merge(WHITE if category_active else TEAL),
                                    **text_merge(INK if category_active else WHITE),
                                    **line_merge(BORDER if category_active else TEAL),
                                }
                            ),
                        }
                    }
                },
            },
        }

    for hidden in ["seller_items_table", "seller_category_chart"]:
        target = (
            "3d9f1a6c2b8e4075a1f3"
            if hidden == "seller_items_table"
            else "c47e2b9d8a1f6053e7b2"
        )
        payload = make(hidden)
        with open(
            f"olist-analysis.Report/definition/bookmarks/{target}.bookmark.json",
            "w",
            encoding="utf-8",
            newline="\n",
        ) as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")


# ---------------------------------------------------------------- main
def main():
    for page in (PAGE1, PAGE2, PAGE3):
        for path in glob.glob(os.path.join(PAGES, page, "visuals", "*", "visual.json")):
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            data = theme_colors(data)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(data, fh, indent=2)
                fh.write("\n")

    page_one()
    page_two()
    page_three()
    theme()
    bookmarks()
    print("redesign applied")


if __name__ == "__main__":
    main()

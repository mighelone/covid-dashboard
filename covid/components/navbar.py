import dash_bootstrap_components as dbc


def get_navbar(brand: str = "COVID-19 Dashboard") -> dbc.NavbarSimple:
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(id="navlink-regioni", children="Regioni", href="/regioni")
            ),
            dbc.NavItem(
                dbc.NavLink(
                    id="navlink-province", children="Province", href="/province"
                )
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Links", header=True),
                    dbc.DropdownMenuItem(
                        "Dati", href="https://github.com/pcm-dpc/COVID-19"
                    ),
                    dbc.DropdownMenuItem(
                        "GeoJson", href="https://github.com/openpolis/geojson-italy"
                    ),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
            dbc.NavItem(dbc.Button("Help", id="help-button")),
        ],
        brand=brand,
        brand_href="#",
        color="dark",
        dark=True,
        fluid=True,
        sticky="top",
        expand=True,
    )

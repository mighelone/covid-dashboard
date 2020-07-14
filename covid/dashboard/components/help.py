import dash_html_components as html
import dash_bootstrap_components as dbc


def get_help_modal():
    """return a help modal component with id: modal-help
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Help"),
            dbc.ModalBody(
                html.Div(
                    [
                        html.H5("Istruzioni"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "Clicca su una regione per aggiornare i"
                                            " grafici a destra."
                                        )
                                    ],
                                    className="li",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Il valore rappresentato nella mappa puo"
                                            " essere cambiato selezionando un nuovo"
                                            " valore dal menu a tendina in alto a"
                                            " sinistra"
                                        )
                                    ],
                                    className="li",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Seleziona la data in alto a sinistra per"
                                            "mostrare il valore nella data selezionata."
                                        )
                                    ],
                                    className="li",
                                ),
                            ],
                            className="ul",
                        ),
                    ]
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-help-button", className="ml-auto",)
            ),
        ],
        id="modal-help",
    )

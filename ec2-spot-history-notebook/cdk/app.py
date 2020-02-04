#!/usr/bin/env python3

from aws_cdk import core

from spot_historic_notebook.spot_historic_notebook_stack import CdkSpotHistoricNotebookStack


app = core.App()
CdkSpotHistoricNotebookStack(app, "Spot-Historic-Notebook")
app.synth()

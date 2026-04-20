# CMIP6

[EN] Sub-repository dedicated to the acquisition and processing of CMIP6 climate projections.

[PT] Subrespositório dedicado à aquisição e processamento das projeções climáticas CMIP6

## Links Importantes
- https://cds.climate.copernicus.eu/how-to-api

## Future Development
### 3_EQM_BIAS.py
- Aggregating climate projections for bias correction based on the hydrological year rather than the calendar year (resample('YS')).
- Maybe: df["hyear"] = df.index.to_period("A-Oct").year (assuming it starts in October)

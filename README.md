# TAMU Digital Collections Identifier Minter

Application for easily minting ARKs, DOIs, and other ids.

## How to Use

### EZID

Create ARKs:

```shell
 tamu_mint create_ark -i test.csv
```

Get an Ark:

```shell
tamu_mint get_ark -a "ark:/81423/m3z462"
```

Switch Statuses:

```shell
 tamu_mint switch_statuses -i forest-service-arks-output.csv -s public
```

### Crossref

For Pending pubs:

```shell
  tamu_mint generate_crossref_deposit -i metadata.csv -t pending_publication
```

For reports:

```shell
 tamu_mint generate_crossref_deposit -i reports.csv -t report
```

## Optional Settings

If you hate putting stuff in over and over again, you can use environmental variables:

```shell
export CROSSREF_DEPOSITOR_NAME="Mark Baggett"
export CROSSREF_DEPOSITOR_EMAIL="mark.baggett@tamu.edu"
export CROSSREF_REGISTRANT="Texas A&M University"

```


import click
from tamu_id_minter import EZIDARKHandler

@click.group()
def cli() -> None:
    pass

@cli.command(
    "create_arks", help="Creates ARKs from a CSV with Metadata"
)
@click.option(
    "--input_csv",
    "-i",
    help="The path to the CSV including ARK metadata",
)
@click.option(
    "--output_csv",
    "-o",
    help="The path to the CSV to write ARK info from EZID",
    default="output.csv",
)
def create_arks(input_csv, output_csv):
    generator = EZIDARKHandler()
    results = generator.create_batch_from_csv(
        input_csv, output_csv
    )
    print(f"Processed {len(results)} records")


@cli.command(
    "get_ark", help="Get metadata about an ARK"
)
@click.option(
    "--ark",
    "-a",
    help="The ARK as ark:/99999/fk4cz3dh0"
)
def get_ark(ark):
    handler = EZIDARKHandler()
    handler.get_ark(ark)

@cli.command(
    "switch_statuses", help="Switch status for all items in a CSV"
)
@click.option(
    "--status",
    "-s",
    help="The status to switch to: public, reserved, unavailable",
    default="public"
)
@click.option(
    "--input_csv",
    "-i",
    help="The path to the CSV including ARK metadata",
)
def switch_statuses(status, input_csv):
    handler = EZIDARKHandler()
    handler.batch_switch_status(input_csv, status)
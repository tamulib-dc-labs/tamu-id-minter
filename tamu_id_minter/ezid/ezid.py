import csv
import requests
import os


class EZIDARKHandler:
    def __init__(self, shoulder_url='https://ezid.cdlib.org/shoulder/ark:/81423/d2'):
        self.url = shoulder_url
        self.headers = {'Content-Type': 'text/plain'}
        self.auth = (os.getenv("EZID_USER"), os.getenv("EZID_PASSWORD"))
        self.completed = []

    def create_metadata(self, who, what, when, where):
        """Create metadata content string for EZID request.

        Args:
            who (str): the agent responsible for the resource — typically the creator, author, or contributor.
            what (str): the title of the work
            when (str): the date of publication for the original work
            where (str): URL or current location of the resource

        Returns:
            dict: The data formatted for the Post and Creation of the Ark
        """
        # @TODO: _status: should not be assumed as reserved
        return (
            f'erc.who: {who}\n'
            f'erc.what: {what}\n'
            f'erc.when: {when}\n'
            f'_target: {where}\n'
            f'_status: reserved\n'
        )

    def create_ark(self, who, what, when, where):
        """Create a single ARK identifier.

        Args:
            who (str): the agent responsible for the resource — typically the creator, author, or contributor.
            what (str): the title of the work
            when (str): the date of publication for the original work
            where (str): URL or current location of the resource

        Returns:
            dict: Data sent to the ARK with the ARK returned
        """
        metadata_content = self.create_metadata(who, what, when, where)
        data = metadata_content.encode('utf-8')

        response = requests.post(self.url, data=data, headers=self.headers, auth=self.auth)
        # https://n2t.net/ark:/81423/d2tg6j
        full_message = response.content.decode('utf-8')
        ark = ""
        if "success" in  full_message:
            ark = f"https://n2t.net/{full_message.split(' ')[-1]}"
        return {
            'who': who,
            'what': what,
            'when': when,
            'where': where,
            'message': full_message,
            'ark': ark,
        }

    def process_csv(self, input_file):
        """Process CSV file and create ARKs for each row.

        Args:

            input_file (str): The CSV that contains your ARK information with appropriate headings.
        """
        with open(input_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                result = self.create_ark(
                    row['who'],
                    row['what'],
                    row['when'],
                    row['where']
                )
                self.completed.append(result)

    def save_results(self, output_file):
        """Save completed results to CSV file."""
        fieldnames = ['who', 'what', 'when', 'where', 'message', 'ark']
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.completed:
                writer.writerow(row)

    def create_batch_from_csv(self, input_file, output_file):
        """Main method to process input and save results."""
        self.process_csv(input_file)
        self.save_results(output_file)
        return self.completed

    def get_ark(self, ark):
        """Prints Metadata About an ARK"""
        response = requests.get(f"https://ezid.cdlib.org/id/{ark}", headers=self.headers, auth=self.auth)
        print(response.content.decode("utf-8"))

    def switch_status(self, ark, status="public"):
        """Switches the Status of a Single ARK
        
        Args:
            ark (str): The ARK you want to modify (i.e. ark:/81423/d2h03s)
            status (str): The status you want to change to. (public by default)

        Returns:
            tuple: bool, message (str)

        Example:
            >>> EZIDARKHandler().switch_status("ark:/81423/d2h03s", "public")

            (True, "ark:/81423/d2h03s status successfully changed to public")
        """
        # @TODO: status should be limited to known values
        metadata_content = (
            f'_status: {status}\n'
        )
        data = metadata_content.encode('utf-8')
        response = requests.post(
            f"https://ezid.cdlib.org/id/{ark}", 
            data=data, 
            headers=self.headers,
            auth=self.auth
        )
        full_message = response.content.decode('utf-8')
        if "success" in  full_message:
            return True, f"{ark} status successfully changed to {status}"
        else:
            return False, f"{ark} status failed with {response.status_code}"



if __name__ == "__main__":
    # input_csv = "quick.csv"
    # output_csv = "output3.csv"
    # generator = EZIDARKHandler()
    # results = generator.run(input_csv, output_csv)
    # print(f"Processed {len(results)} records")
    ark = "ark:/81423/d2h03s"
    handler = EZIDARKHandler()
    results = handler.switch_status(ark)
    print(results)

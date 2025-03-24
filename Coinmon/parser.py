import zipfile, csv, json

def parse():
    with zipfile.ZipFile("data.zip", "r") as archive:
        result = {}
        targets = [
            "Binance",
            "OKX",
            "UpBit",
            "Coinbase",
            "FTX",
            "KuCoin",
            "Crypto.com",
            "Huobi",
            "Kraken",
            "Gate.io"
        ]

        # Load original JSON
        with open("exchanges.json", "r", encoding="utf-8") as json_file:
            result = json.load(json_file)

        # Open Coinmon files
        for file in archive.namelist():
            with zipfile.Path(archive, file).open(mode="r", encoding="utf-8") as dataFile:
                reader = csv.DictReader(dataFile)

                for row in reader:
                    if "label" in row and "address" in row:
                        label = row["label"].lower()
                        if any(match.lower() in label for match in targets):
                            result.setdefault(row["address"], row["label"])

        with open("exchanges.json", "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=4)

parse()
